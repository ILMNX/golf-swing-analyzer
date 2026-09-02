package main

import (
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
)

const (
	serverPort  = ":3000"
	mlEngineURL = "http://127.0.0.1:8000/analyze-swing"
	tempDir     = "."
	tempPrefix  = "temp_swing_"
)

// SwingMetrics holds per-dimension scores from pose analysis.
type SwingMetrics struct {
	Tempo    int `json:"tempo"`
	Posture  int `json:"posture"`
	Rotation int `json:"rotation"`
	Balance  int `json:"balance"`
}

// SwingAnalysis is the full response sent to the frontend.
type SwingAnalysis struct {
	Status         string       `json:"status"`
	Score          int          `json:"score"`
	Recommendation string       `json:"recommendation"`
	Club           string       `json:"club"`
	ShotType       string       `json:"shot_type"`
	Metrics        SwingMetrics `json:"metrics"`
	AnalyzedAt     string       `json:"analyzed_at"`
	Filename       string       `json:"filename"`
}

// mlEngineResponse mirrors the JSON shape returned by the Python ML engine.
type mlEngineResponse struct {
	Status         string `json:"status"`
	Score          int    `json:"score"`
	Recommendation string `json:"recommendation"`
}

func main() {
	app := fiber.New(fiber.Config{
		BodyLimit: 100 * 1024 * 1024, // 100 MB
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

	var mlResult mlEngineResponse
	resp, err := client.R().
		SetFile("video", tmpPath).
		SetFormData(map[string]string{
			"club":      club,
			"shot_type": shotType,
		}).
		SetResult(&mlResult).
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

	// Enrich ML response with config + derived metrics for the report page.
	// TODO: replace mock metrics with real values from ML engine once implemented.
	result := SwingAnalysis{
		Status:         mlResult.Status,
		Score:          mlResult.Score,
		Recommendation: mlResult.Recommendation,
		Club:           club,
		ShotType:       shotType,
		Filename:       fileHeader.Filename,
		AnalyzedAt:     time.Now().UTC().Format(time.RFC3339),
		Metrics: SwingMetrics{
			Tempo:    mlResult.Score - 3,
			Posture:  mlResult.Score - 7,
			Rotation: mlResult.Score + 5,
			Balance:  mlResult.Score,
		},
	}

	return c.JSON(result)
}
