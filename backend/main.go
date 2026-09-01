package main

import (
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"

	"github.com/go-resty/resty/v2"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/logger"
)

const (
	serverPort   = ":3000"
	mlEngineURL  = "http://127.0.0.1:8000/analyze-swing"
	tempDir      = "."
	tempPrefix   = "temp_swing_"
)

// SwingAnalysis mirrors the JSON shape returned by the ML engine.
type SwingAnalysis struct {
	Status         string `json:"status"`
	Score          int    `json:"score"`
	Recommendation string `json:"recommendation"`
}

func main() {
	app := fiber.New(fiber.Config{
		BodyLimit: 100 * 1024 * 1024, // 100 MB — accommodate video uploads
	})

	app.Use(logger.New())

	app.Get("/health", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{"status": "ok"})
	})

	app.Post("/upload-swing", handleUploadSwing)

	log.Printf("Go backend listening on %s", serverPort)
	log.Fatal(app.Listen(serverPort))
}

// handleUploadSwing accepts a video file, forwards it to the ML engine,
// and returns the analysis result to the client.
func handleUploadSwing(c *fiber.Ctx) error {
	// -----------------------------------------------------------------------
	// 1. Receive the uploaded file from multipart form-data
	// -----------------------------------------------------------------------
	fileHeader, err := c.FormFile("video")
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "missing 'video' field in form-data",
		})
	}

	src, err := fileHeader.Open()
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": fmt.Sprintf("failed to open upload: %v", err),
		})
	}
	defer src.Close()

	// -----------------------------------------------------------------------
	// 2. Save to a temporary file on disk
	// -----------------------------------------------------------------------
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

	// Ensure the temp file is always removed, even on error paths
	defer func() {
		tmpFile.Close()
		os.Remove(tmpPath)
	}()

	if _, err = io.Copy(tmpFile, src); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": fmt.Sprintf("failed to write temp file: %v", err),
		})
	}

	// Close before forwarding so the ML engine can read the file cleanly
	if err = tmpFile.Close(); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": fmt.Sprintf("failed to close temp file: %v", err),
		})
	}

	// -----------------------------------------------------------------------
	// 3. Forward the video to the Python ML engine via go-resty
	// -----------------------------------------------------------------------
	client := resty.New()

	var result SwingAnalysis
	resp, err := client.R().
		SetFile("video", tmpPath).
		SetResult(&result).
		Post(mlEngineURL)

	if err != nil {
		return c.Status(fiber.StatusBadGateway).JSON(fiber.Map{
			"error": fmt.Sprintf("ML engine unreachable: %v", err),
		})
	}

	if resp.IsError() {
		return c.Status(fiber.StatusBadGateway).JSON(fiber.Map{
			"error": fmt.Sprintf("ML engine returned %d: %s", resp.StatusCode(), resp.String()),
		})
	}

	// -----------------------------------------------------------------------
	// 4. Return the ML engine's JSON response to the client
	// -----------------------------------------------------------------------
	return c.JSON(result)
}
