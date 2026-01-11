package main

import (
	"fmt"
	"time"
)

// Scroll represents a memory or flare event scroll
type Scroll struct {
	ID             string    `json:"id"`
	Trigger        string    `json:"trigger"`
	Timestamp      time.Time `json:"timestamp"`
	TrustScore     float64   `json:"trust_score"`
	GeneticMarkers []string  `json:"genetic_markers"`
}

// GeneInterventionPlan represents a CRISPR-style simulation outcome
type GeneInterventionPlan struct {
	MutationLoopID      string   `json:"mutation_loop_id"`
	TargetedGenes       []string `json:"targeted_genes"`
	TrustAligned        bool     `json:"trust_aligned"`
	RequiredRecalibrate bool     `json:"required_recalibrate"`
	PredictedRelief     float64  `json:"predicted_relief,omitempty"`
	FlareSuppression    float64  `json:"flare_suppression,omitempty"`
	RebirthEligible     bool     `json:"rebirth_eligible,omitempty"`
}

// StartScrollSimulation initializes a new scroll simulation
func StartScrollSimulation(scroll Scroll) GeneInterventionPlan {
	// Logic:
	// Low trust, no markers -> TrustAligned = false, RequiredRecalibrate = true, MutationLoopID = "discovery_loop"
	// High trust + flare + markers -> TrustAligned = true, RequiredRecalibrate = false, MutationLoopID = "flare_mutation_loop"

	if scroll.TrustScore < 0.7 && len(scroll.GeneticMarkers) == 0 {
		return GeneInterventionPlan{
			MutationLoopID:      "discovery_loop",
			TargetedGenes:       []string{},
			TrustAligned:        false,
			RequiredRecalibrate: true,
		}
	}

	if scroll.TrustScore >= 0.7 && scroll.Trigger == "flare" && len(scroll.GeneticMarkers) > 0 {
		return GeneInterventionPlan{
			MutationLoopID:      "flare_mutation_loop",
			TargetedGenes:       scroll.GeneticMarkers,
			TrustAligned:        true,
			RequiredRecalibrate: false,
			PredictedRelief:     0.87,
			FlareSuppression:    0.91,
			RebirthEligible:     true,
		}
	}

	// Default fallback
	fmt.Printf("Scroll %s falling back to default/compost\n", scroll.ID)
	return GeneInterventionPlan{
		MutationLoopID:      "compost_stream",
		RequiredRecalibrate: true,
	}
}
