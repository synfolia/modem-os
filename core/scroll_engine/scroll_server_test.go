package scroll_engine

import (
	"testing"

	"Maple-OS/modem_os/core/shared/types"
)

func TestStartScrollSimulation_LowTrustNoMarkers(t *testing.T) {
	scroll := types.Scroll{
		ID:             "test_low_trust",
		TrustScore:     0.12,
		IsFlareEvent:   false,
		GeneticMarkers: []string{},
	}

	out := StartScrollSimulation(scroll)

	if out.TrustAligned {
		t.Fatalf("expected TrustAligned=false for low trust")
	}
	if !out.RequiredRecalibrate {
		t.Fatalf("expected RequiredRecalibrate=true when low trust or missing markers")
	}
	if out.MutationLoopID != "discovery_loop" {
		t.Fatalf("expected discovery_loop, got %q", out.MutationLoopID)
	}
}

func TestStartScrollSimulation_FlareMarkersHighTrust(t *testing.T) {
	scroll := types.Scroll{
		ID:             "test_high_trust",
		TrustScore:     0.92,
		IsFlareEvent:   true,
		GeneticMarkers: []string{"g1", "g2"},
	}

	out := StartScrollSimulation(scroll)

	if !out.TrustAligned {
		t.Fatalf("expected TrustAligned=true for high trust")
	}
	if out.RequiredRecalibrate {
		t.Fatalf("expected RequiredRecalibrate=false for high trust + markers")
	}
	if out.MutationLoopID != "flare_mutation_loop" {
		t.Fatalf("expected flare_mutation_loop, got %q", out.MutationLoopID)
	}
}
