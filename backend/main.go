package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/fiber/v2/middleware/proxy"
)

const (
	serverPort    = ":3000"
	mlEngineURL   = "http://127.0.0.1:8000/analyze-swing"
	mlEngineBase  = "http://127.0.0.1:8000"
	tempDir     = "."
	tempPrefix  = "temp_swing_"
)

func main() {
	app := fiber.New(fiber.Config{
		BodyLimit: 100 * 1024 * 1024,
	})

	app.Use(logger.New())
	app.Use(cors.New(cors.Config{
		AllowOrigins: "http://localhost:5173,http://127.0.0.1:5173",
		AllowHeaders: "Origin, Content-Type, Accept",
	}))

	app.Get("/health", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{"status": "ok"})
	})

	app.Post("/upload-swing", handleUploadSwing)

	// Proxy annotated analysis videos from ML engine
	app.Get("/outputs/*", func(c *fiber.Ctx) error {
		path := c.Params("*")
		return proxy.Do(c, mlEngineBase+"/outputs/"+path)
	})

	log.Printf("Go backend listening on %s", serverPort)
	log.Fatal(app.Listen(serverPort))
}

func handleUploadSwing(c *fiber.Ctx) error {
	fileHeader, err := c.FormFile("video")
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "missing 'video' field in form-data",
		})
	}

	club := c.FormValue("club", "iron_7")
	shotType := c.FormValue("shot_type", "full_swing")

	src, err := fileHeader.Open()
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": fmt.Sprintf("failed to open upload: %v", err),
		})
	}
	defer src.Close()

	ext := filepath.Ext(fileHeader.Filename)
	if ext == "" {
		ext = ".mp4"
	}

	tmpFile, err := os.CreateTemp(tempDir, tempPrefix+"*"+ext)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": fmt.Sprintf("failed to create temp file: %v", err),
		})
	}
	tmpPath := tmpFile.Name()

	defer func() {
		tmpFile.Close()
		os.Remove(tmpPath)
	}()

	if _, err = io.Copy(tmpFile, src); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": fmt.Sprintf("failed to write temp file: %v", err),
		})
	}

	if err = tmpFile.Close(); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": fmt.Sprintf("failed to close temp file: %v", err),
		})
	}

	client := resty.New()
	client.SetTimeout(5 * time.Minute)

	resp, err := client.R().
		SetFile("video", tmpPath).
		SetFormData(map[string]string{
			"club":      club,
			"shot_type": shotType,
		}).
		Post(mlEngineURL)

	if err != nil {
		return c.Status(fiber.StatusBadGateway).JSON(fiber.Map{
			"error": fmt.Sprintf("ML engine unreachable: %v", err),
		})
	}

	var mlResult map[string]interface{}
	if err := json.Unmarshal(resp.Body(), &mlResult); err != nil {
		return c.Status(fiber.StatusBadGateway).JSON(fiber.Map{
			"error": "invalid response from ML engine",
		})
	}

	if resp.StatusCode() == 422 {
		return c.Status(fiber.StatusUnprocessableEntity).JSON(mlResult)
	}

	if resp.IsError() {
		return c.Status(fiber.StatusBadGateway).JSON(fiber.Map{
			"error": fmt.Sprintf("ML engine returned %d: %s", resp.StatusCode(), resp.String()),
		})
	}

	mlResult["club"] = club
	mlResult["shot_type"] = shotType
	mlResult["filename"] = fileHeader.Filename
	mlResult["analyzed_at"] = time.Now().UTC().Format(time.RFC3339)

	return c.JSON(mlResult)
}
