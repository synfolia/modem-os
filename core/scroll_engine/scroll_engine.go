package core

import (
	"fmt"
	"time"
)

// Scroll represents a memory or flare event scroll
type Scroll struct {
	ID             string
	Trigger        string
	Timestamp      time.Time
	TrustScore     float64
	GeneticMarkers []string
}

// GeneInterventionPlan represents a CRISPR-style simulation outcome
type GeneInterventionPlan struct {
	TargetGenes      []string
	MutationLoopID   string
	PredictedRelief  float64
	FlareSuppression float64
	RebirthEligible  bool
}

// StartScrollSimulation begins a new trial based on scroll history
func StartScrollEngineSimulation(scroll Scroll) GeneInterventionPlan {
	fmt.Println("Starting engine simulation for scroll:", scroll.ID)

	if scroll.TrustScore < 0.7 {
		fmt.Println("Scroll trust too low. Composting instead...")
		CompostScroll(scroll)
		return GeneInterventionPlan{}
	}

	if scroll.Trigger == "flare" && contains(scroll.GeneticMarkers, "ATG16L1") {
		return TriggerGeneIntervention(scroll)
	}

	fmt.Println("No eligible gene targets found. Scroll held in memory.")
	return GeneInterventionPlan{}
}

// TriggerGeneIntervention simulates CRISPR mutation loop for flare correction
func TriggerGeneIntervention(scroll Scroll) GeneInterventionPlan {
	fmt.Println("Triggering gene intervention based on scroll-to-gene alignment...")

	return GeneInterventionPlan{
		TargetGenes:      []string{"ATG16L1", "TNFSF15"},
		MutationLoopID:   "coconut_loop_001",
		PredictedRelief:  0.87,
		FlareSuppression: 0.91,
		RebirthEligible:  true,
	}
}

// CompostScroll marks a scroll for decay if trust or clarity is too low
func CompostScroll(scroll Scroll) {
	fmt.Printf("Composting scroll %s due to low trust or outcome drift\n", scroll.ID)
}

// contains helper
func contains(slice []string, val string) bool {
	for _, item := range slice {
		if item == val {
			return true
		}
	}
	return false
}
