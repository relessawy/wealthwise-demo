package com.acme.wealthwise;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class SavingsGuidanceTest {
  private SavingsGuidance.Result calculate(String target, String saved, int months) {
    return SavingsGuidance.calculate(new BigDecimal(target), new BigDecimal(saved), months);
  }
  @Test void sampleMonthlyContribution() {
    var result = calculate("1200.00", "300.00", 6);
    assertEquals(new BigDecimal("900.00"), result.remaining());
    assertEquals(new BigDecimal("150.00"), result.monthlyContribution());
    // WW-1: assert the actionable guidance shown in WealthWise as well.
    assertEquals("Set a regular savings goal and review your progress.", result.guidance());
  }
  @Test void roundsUpToReachTarget() {
    assertEquals(new BigDecimal("33.34"), calculate("100", "0", 3).monthlyContribution());
  }
  @Test void reachedGoalNeverProducesNegativeContribution() {
    assertEquals(new BigDecimal("0.00"), calculate("100", "125", 3).monthlyContribution());
  }
  @Test void rejectsInvalidInputs() {
    for (int months : new int[]{0, -1, 121})
      assertThrows(jakarta.ws.rs.BadRequestException.class, () -> calculate("1200", "300", months));
    for (String amount : new String[]{"-1", "0.001", "10000001"}) {
      assertThrows(jakarta.ws.rs.BadRequestException.class, () -> calculate(amount, "0", 6));
      assertThrows(jakarta.ws.rs.BadRequestException.class, () -> calculate("1200", amount, 6));
    }
  }
}
