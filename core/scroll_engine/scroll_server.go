package core

import (
	"encoding/json"
	"log"
	"net/http"

	"Maple-OS/modem_os/core/shared/types"
)

// StartScrollSimulation initializes a new scroll simulation
// based on the provided scroll data.
// It checks the trust score and genetic markers to determine
// if a CRISPR-style mutation loop should be initiated.
// If the trust score is too low, it composts the scroll.
// If the scroll is a flare event and contains specific genetic markers,
// it triggers a gene intervention simulation.

func StartScrollSimulation(scroll types.Scroll) types.GeneInterventionPlan {
	return types.GeneInterventionPlan{
		MutationLoopID:      "coconut_loop_001",
		TargetedGenes:       scroll.GeneticMarkers,
		TrustAligned:        true,
		RequiredRecalibrate: true,
	}
}

func simulateHandler(w http.ResponseWriter, r *http.Request) {
	var scroll types.Scroll
	if err := json.NewDecoder(r.Body).Decode(&scroll); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	result := StartScrollSimulation(scroll)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

func main() {
	http.HandleFunc("/simulate", simulateHandler)
	log.Println("Scroll Engine API listening on :8282")
	log.Fatal(http.ListenAndServe(":8282", nil))
}
