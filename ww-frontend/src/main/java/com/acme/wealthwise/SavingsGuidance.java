package com.acme.wealthwise;

import java.math.BigDecimal;
import java.math.RoundingMode;
import jakarta.ws.rs.BadRequestException;

/** Deterministic training calculator; no customer data or investment advice. */
public final class SavingsGuidance {
  private SavingsGuidance() {}
  public record Result(BigDecimal target, BigDecimal saved, int months,
      BigDecimal remaining, BigDecimal monthlyContribution, String guidance,
      String disclaimer) {}

  public static Result calculate(BigDecimal target, BigDecimal saved, int months) {
    if (target == null || saved == null || target.signum() < 0 || saved.signum() < 0
        || target.compareTo(new BigDecimal("10000000")) > 0
        || saved.compareTo(new BigDecimal("10000000")) > 0
        || target.scale() > 2 || saved.scale() > 2 || months < 1 || months > 120) {
      throw new BadRequestException("Use amounts from 0 to 10000000 with at most two decimal places, and 1 to 120 months.");
    }
    BigDecimal remaining = target.subtract(saved).max(BigDecimal.ZERO).setScale(2);
    BigDecimal monthly = remaining.divide(BigDecimal.valueOf(months), 2, RoundingMode.CEILING);
    return new Result(target, saved, months, remaining, monthly, guidance(monthly, months),
        "Illustrative training calculation only. No interest, fees or financial advice.");
  }

  static String guidance(BigDecimal monthly, int months) {
    // WW-1: replace this generic guidance with the calculated monthly action.
    return "Set a regular savings goal and review your progress.";
  }
}
