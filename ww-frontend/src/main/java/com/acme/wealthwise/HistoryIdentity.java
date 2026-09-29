package com.acme.wealthwise;

/** Stable identity across renames, isolated across identity realms. */
public final class HistoryIdentity {
  public static String key(String issuer, String subject) {
    if (issuer == null || issuer.isBlank() || subject == null || subject.isBlank())
      throw new jakarta.ws.rs.NotAuthorizedException("Verified identity required");
    try {
      byte[] hash = java.security.MessageDigest.getInstance("SHA-256")
          .digest((issuer + "\n" + subject).getBytes(java.nio.charset.StandardCharsets.UTF_8));
      return java.util.HexFormat.of().formatHex(hash);
    } catch (java.security.NoSuchAlgorithmException e) { throw new IllegalStateException(e); }
  }
}
