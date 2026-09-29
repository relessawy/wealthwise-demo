package com.wealthwise.ui;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.config.inject.ConfigProperty;

/** Authenticated synthetic request; never changes customer/application state. */
@Path("/api/demo/operational-check")
public class OperationalCheckResource {
  @ConfigProperty(name="wealthwise.demo.operational-check", defaultValue="false")
  boolean enabled;

  @GET
  public Response check(@QueryParam("fail") boolean fail) {
    if (!enabled) return Response.status(404).build();
    return Response.status(fail ? 500 : 200)
        .entity(java.util.Map.of("status", fail ? "controlled-demo-error" : "healthy",
            "synthetic", true)).build();
  }
}
