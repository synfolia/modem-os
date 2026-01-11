package main

import (
	"testing"
	"time"
)

func TestStartScrollSimulation(t *testing.T) {
	// Case 1: Low trust, no markers
	lowTrustScroll := Scroll{
		ID:             "test_low_trust",
		Trigger:        "memory",
		Timestamp:      time.Now(),
		TrustScore:     0.2,
		GeneticMarkers: []string{},
	}

	result1 := StartScrollSimulation(lowTrustScroll)

	if result1.TrustAligned != false {
		t.Errorf("Expected TrustAligned to be false, got %v", result1.TrustAligned)
	}
	if result1.RequiredRecalibrate != true {
		t.Errorf("Expected RequiredRecalibrate to be true, got %v", result1.RequiredRecalibrate)
	}
	if result1.MutationLoopID != "discovery_loop" {
		t.Errorf("Expected MutationLoopID to be discovery_loop, got %s", result1.MutationLoopID)
	}

	// Case 2: High trust + flare + markers
	highTrustScroll := Scroll{
		ID:             "test_high_trust",
		Trigger:        "flare",
		Timestamp:      time.Now(),
		TrustScore:     0.8,
		GeneticMarkers: []string{"ATG16L1"},
	}

	result2 := StartScrollSimulation(highTrustScroll)

	if result2.TrustAligned != true {
		t.Errorf("Expected TrustAligned to be true, got %v", result2.TrustAligned)
	}
	if result2.RequiredRecalibrate != false {
		t.Errorf("Expected RequiredRecalibrate to be false, got %v", result2.RequiredRecalibrate)
	}
	if result2.MutationLoopID != "flare_mutation_loop" {
		t.Errorf("Expected MutationLoopID to be flare_mutation_loop, got %s", result2.MutationLoopID)
	}
}
