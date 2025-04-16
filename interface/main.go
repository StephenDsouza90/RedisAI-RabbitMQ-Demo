package main

import (
	"os"

	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	"github.com/gin-gonic/gin"
)

func main() {
	// Get from env variable
	connString := os.Getenv("RABBITMQ_URL")
	queueName := os.Getenv("RABBITMQ_QUEUE")
	filePath := os.Getenv("FILE_PATH")
	mlUrl := os.Getenv("ML_URL")

	// Initialize RabbitMQ connection
	rabbitMQ, err := NewRabbitMQ(connString, queueName)
	if err != nil {
		panic(err)
	}
	defer rabbitMQ.Close()

	handler := NewHandler(rabbitMQ)

	r := gin.Default()
	r.POST("/upload", func(c *gin.Context) {
		handler.UploadFile(c, queueName, filePath)
	})
	r.POST("/predict", func(c *gin.Context) {
		handler.Predict(c, mlUrl)
	})
	r.GET("/health", handler.HealthCheck)
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// Start the server
	r.Run(":8080")
}
