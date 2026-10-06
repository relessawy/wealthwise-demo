package com.wealthwise.ui;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.ws.rs.container.*;
import jakarta.ws.rs.core.*;
import java.lang.reflect.Proxy;
import java.nio.file.*;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import static org.junit.jupiter.api.Assertions.*;
class RequestEventFilterTest {
 @TempDir Path dir;
 @SuppressWarnings("unchecked") static <T> T proxy(Class<T> type, java.util.function.Function<String,Object> f) {
  return (T) Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[]{type},(p,m,a)->f.apply(m.getName()));
 }
 @Test void apiEventsHaveOnlyApprovedFieldsWithEitherPathForm() throws Exception {
  var filter=new RequestEventFilter();filter.mapper=new ObjectMapper();filter.file=Optional.of(dir.resolve("events").toString());filter.service="wealthwise";filter.environment="demo";
  for(String path:new String[]{"api/demo/check","/api/demo/check"}) {
   var headers=new MultivaluedHashMap<String,Object>();
   var uri=proxy(UriInfo.class,n->path);
   var request=proxy(ContainerRequestContext.class,n->uri);
   var response=proxy(ContainerResponseContext.class,n->n.equals("getStatus")?500:headers);
   filter.filter(request,response);
   assertNotNull(headers.getFirst("X-Request-ID"));
  }
  var lines=Files.readAllLines(Path.of(filter.file.orElseThrow()));assertEquals(2,lines.size());
  var event=filter.mapper.readTree(lines.get(0));assertEquals(6,event.size());assertEquals(500,event.get("status").asInt());
  assertFalse(event.has("username"));assertFalse(event.has("body"));assertFalse(event.has("authorization"));
 }
 @Test void disabledLoggingDoesNotAccessRequestOrResponse() {
  var filter=new RequestEventFilter();
  for(var value:java.util.List.of(Optional.<String>empty(),Optional.of(" "))) {
   filter.file=value;filter.filter(null,null);
  }
 }
 @Test void staticPageDoesNotProduceAnApiEvent() {
  var filter=new RequestEventFilter();filter.file=Optional.of(dir.resolve("events").toString());
  var uri=proxy(UriInfo.class,n->"/index.html");filter.filter(proxy(ContainerRequestContext.class,n->uri),null);
  assertFalse(Files.exists(Path.of(filter.file.orElseThrow())));
 }
}
