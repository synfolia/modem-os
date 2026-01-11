package scroll_engine

import (
	"fmt"

	"Maple-OS/modem_os/core/shared/types"
)

// StartScrollSimulation initializes a new scroll simulation.
func StartScrollSimulation(scroll types.Scroll) types.GeneInterventionPlan {
	trustAligned := scroll.TrustScore >= 0.7
	hasMarkers := len(scroll.GeneticMarkers) > 0

	// Low trust + no markers → discovery loop + recalibration
	if !trustAligned && !hasMarkers {
		return types.GeneInterventionPlan{
			MutationLoopID:      "discovery_loop",
			TargetedGenes:       []string{},
			TrustAligned:        false,
			RequiredRecalibrate: true,
		}
	}

	// High trust + flare + markers → flare mutation loop
	if trustAligned && scroll.IsFlareEvent && hasMarkers {
		return types.GeneInterventionPlan{
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
	fmt.Printf("Scroll %s falling back to compost stream\n", scroll.ID)
	return types.GeneInterventionPlan{
		MutationLoopID:      "compost_stream",
		TargetedGenes:       scroll.GeneticMarkers,
		TrustAligned:        trustAligned,
		RequiredRecalibrate: true,
	}
}
