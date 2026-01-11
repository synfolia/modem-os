package types

type Scroll struct {
	ID             string   `json:"id"`
	TrustScore     float64  `json:"trust_score"`
	IsFlareEvent   bool     `json:"is_flare_event"`
	GeneticMarkers []string `json:"genetic_markers"`
}

type GeneInterventionPlan struct {
	MutationLoopID      string   `json:"mutation_loop_id"`
	TargetedGenes       []string `json:"targeted_genes"`
	TrustAligned        bool     `json:"trust_aligned"`
	RequiredRecalibrate bool     `json:"required_recalibrate"`

	PredictedRelief  float64 `json:"predicted_relief,omitempty"`
	FlareSuppression float64 `json:"flare_suppression,omitempty"`
	RebirthEligible  bool    `json:"rebirth_eligible,omitempty"`
}
