package com.acme.wealthwise;

public final class DemoAdvice {
  public static String answer(String message) {
    return switch (message) {
          case "Conservative" -> "Illustrative mix: 80% bonds, 20% stocks.";
          case "Balanced" -> "Illustrative mix: 50% bonds, 50% stocks.";
          case "Aggressive" -> "Illustrative mix: 20% bonds, 80% stocks.";
          default ->
              throw new jakarta.ws.rs.BadRequestException(
                  "Choose Conservative, Balanced or Aggressive");
        }
        + "\n\n**Demonstration data — not live AI or financial advice.**";
  }
}
