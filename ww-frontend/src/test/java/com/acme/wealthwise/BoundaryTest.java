package com.acme.wealthwise;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class BoundaryTest {
  @Test
  void untrustedIdentityRejected() {
    assertThrows(jakarta.ws.rs.NotAuthorizedException.class, () -> Remote.user("alice\nadmin"));
  }

  @Test
  void missingIdentityRejected() {
    assertThrows(jakarta.ws.rs.NotAuthorizedException.class, () -> Remote.user(null));
  }
}
