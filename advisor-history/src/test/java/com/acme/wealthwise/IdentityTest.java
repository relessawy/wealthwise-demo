package com.acme.wealthwise;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class IdentityTest {
  @Test
  void missingIdentityRejected() {
    assertThrows(jakarta.ws.rs.NotAuthorizedException.class, () -> HistoryResource.owner(null));
  }

  @Test
  void malformedIdentityRejected() {
    assertThrows(
        jakarta.ws.rs.NotAuthorizedException.class, () -> HistoryResource.owner("../alice"));
  }

  @Test
  void validIdentityAccepted() {
    assertEquals("alice", HistoryResource.owner("alice"));
  }
}
