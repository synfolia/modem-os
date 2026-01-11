package scroll_engine

import (
	"encoding/json"
	"log"
	"net/http"

	"Maple-OS/modem_os/core/shared/types"
)

func simulateHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var scroll types.Scroll
	if err := json.NewDecoder(r.Body).Decode(&scroll); err != nil {
		http.Error(w, "invalid input", http.StatusBadRequest)
		return
	}

	result := StartScrollSimulation(scroll)

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(result)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

// Optional but nice: self-describing schema endpoint
func schemaHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]any{
		"endpoints": map[string]any{
			"/health": map[string]string{
				"method": "GET",
				"desc":   "service health check",
			},
			"/simulate": map[string]string{
				"method": "POST",
				"desc":   "run scroll simulation and return a GeneInterventionPlan",
			},
			"/schema": map[string]string{
				"method": "GET",
				"desc":   "self-description of the service",
			},
		},
		"types": map[string]any{
			"Scroll":               "core/shared/types.Scroll",
			"GeneInterventionPlan": "core/shared/types.GeneInterventionPlan",
		},
	})
}

func StartServer(addr string) error {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", healthHandler)
	mux.HandleFunc("/schema", schemaHandler)
	mux.HandleFunc("/simulate", simulateHandler)

	log.Printf("Scroll Engine API listening on %s", addr)
	return http.ListenAndServe(addr, mux)
}
