package com.acme.wealthwise;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class AdviceTest {
  @Test
  void responseIsExplicitlyDemonstration() {
    assertTrue(DemoAdvice.answer("Balanced").toLowerCase().contains("demonstration"));
  }

  @Test
  void invalidRiskRejected() {
    assertThrows(jakarta.ws.rs.BadRequestException.class, () -> DemoAdvice.answer("Hello!"));
  }

  @Test
  void risksProduceDifferentAnswers() {
    assertNotEquals(DemoAdvice.answer("Conservative"), DemoAdvice.answer("Aggressive"));
  }
}
