package com.acme.wealthwise;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class AdviceTest {
  @Test
  void responseIsExplicitlyDemonstration() {
    assertTrue(DemoAdvice.answer("Balanced").toLowerCase().contains("demonstration"));
  }

  @Test
  void responseIsDeterministic() {
    assertEquals(DemoAdvice.answer("budget"), DemoAdvice.answer("budget"));
  }
}
