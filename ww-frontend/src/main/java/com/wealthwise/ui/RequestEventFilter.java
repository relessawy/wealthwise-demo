package com.wealthwise.ui;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.inject.Inject;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerResponseContext;
import jakarta.ws.rs.container.ContainerResponseFilter;
import jakarta.ws.rs.ext.Provider;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.logging.Logger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

/** One completion event for a JAX-RS API request, with no personal/session data. */
@Provider
public class RequestEventFilter implements ContainerResponseFilter {
  private static final Logger LOG=Logger.getLogger(RequestEventFilter.class);
  private static final Object LOCK=new Object();
  @Inject ObjectMapper mapper;
  @ConfigProperty(name="wealthwise.request-events.file") Optional<String> file;
  @ConfigProperty(name="wealthwise.request-events.service", defaultValue="wealthwise") String service;
  @ConfigProperty(name="wealthwise.request-events.environment", defaultValue="demo") String environment;
  public void filter(ContainerRequestContext req, ContainerResponseContext res) {
    if(file.isEmpty() || file.get().isBlank() || !req.getUriInfo().getPath().replaceFirst("^/", "").startsWith("api/")) return;
    String requestId=UUID.randomUUID().toString();
    res.getHeaders().putSingle("X-Request-ID",requestId);
    try {
      String event=mapper.writeValueAsString(Map.of("event_type","http_request_completed",
          "service",service,"environment",environment,"status",res.getStatus(),
          "request_id",requestId,"timestamp",java.time.Instant.now().toString()));
      synchronized(LOCK) {
        // Bound ephemeral growth. Stop recording instead of overwriting unread events.
        Path path=Path.of(file.get());
        if(Files.exists(path) && Files.size(path)>5*1024*1024) { LOG.warn("Request event demo buffer is full"); return; }
        Files.writeString(path,event+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);
      }
    } catch(Exception e) { LOG.warn("Request event could not be recorded"); }
  }
}
