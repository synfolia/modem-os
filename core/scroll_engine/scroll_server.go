package main

import (
	"encoding/json"
	"log"
	"net/http"
	"time"
)

func simulateHandler(w http.ResponseWriter, r *http.Request) {
	var scroll Scroll
	if err := json.NewDecoder(r.Body).Decode(&scroll); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	result := StartScrollSimulation(scroll)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "OK"})
}

func schemaHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	schema := map[string]interface{}{
		"description": "Scroll Engine API for processing memory scrolls and triggering gene interventions.",
		"endpoints": []map[string]string{
			{
				"method":      "POST",
				"path":        "/simulate",
				"description": "Submits a scroll for simulation.",
			},
			{
				"method":      "GET",
				"path":        "/health",
				"description": "Health check.",
			},
			{
				"method":      "GET",
				"path":        "/schema",
				"description": "Returns this schema.",
			},
		},
		"types": map[string]interface{}{
			"Scroll": Scroll{
				ID:             "example_id",
				Trigger:        "flare",
				Timestamp:      time.Now(),
				TrustScore:     0.8,
				GeneticMarkers: []string{"ATG16L1"},
			},
			"GeneInterventionPlan": GeneInterventionPlan{
				MutationLoopID:      "flare_mutation_loop",
				TargetedGenes:       []string{"ATG16L1"},
				TrustAligned:        true,
				RequiredRecalibrate: false,
			},
		},
	}
	json.NewEncoder(w).Encode(schema)
}

func main() {
	http.HandleFunc("/simulate", simulateHandler)
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/schema", schemaHandler)
	log.Println("Scroll Engine API listening on :8282")
	log.Fatal(http.ListenAndServe(":8282", nil))
}
