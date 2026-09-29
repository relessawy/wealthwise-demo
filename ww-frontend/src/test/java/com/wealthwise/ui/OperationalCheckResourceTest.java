package com.wealthwise.ui;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class OperationalCheckResourceTest {
 @Test void disabledByDefault() {var r=new OperationalCheckResource();assertEquals(404,r.check(true).getStatus());}
 @Test void controlledFailureDoesNotPersist() {var r=new OperationalCheckResource();r.enabled=true;assertEquals(500,r.check(true).getStatus());assertEquals(200,r.check(false).getStatus());}
}
