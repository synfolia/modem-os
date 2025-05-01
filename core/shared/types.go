package shared

// Scroll represents the genetic markers and other data for a scroll.
type Scroll struct {
	GeneticMarkers []string `json:"genetic_markers"`
	// Add other fields as needed
}

// GeneInterventionPlan represents the result of a scroll simulation.
type GeneInterventionPlan struct {
	MutationLoopID      string   `json:"mutation_loop_id"`
	TargetedGenes       []string `json:"targeted_genes"`
	TrustAligned        bool     `json:"trust_aligned"`
	RequiredRecalibrate bool     `json:"required_recalibrate"`
}

// Move this code to a new file in the scroll_engine package
