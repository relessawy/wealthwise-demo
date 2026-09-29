package com.acme.wealthwise;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
class HistoryIdentityTest {
 @Test void sameSubjectInDifferentRealmsCannotShareHistory() {
  assertNotEquals(HistoryIdentity.key("https://issuer/realms/a","alice-id"),HistoryIdentity.key("https://issuer/realms/b","alice-id"));
 }
 @Test void stableWithinRealmAndFitsDatabase() {
  String key=HistoryIdentity.key("https://issuer/realms/a","alice-id");
  assertEquals(64,key.length()); assertEquals(key,HistoryIdentity.key("https://issuer/realms/a","alice-id"));
 }
 @Test void absentSubjectRejected() {assertThrows(jakarta.ws.rs.NotAuthorizedException.class,()->HistoryIdentity.key("https://issuer",null));}
}
