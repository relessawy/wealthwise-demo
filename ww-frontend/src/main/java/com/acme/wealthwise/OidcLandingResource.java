package com.acme.wealthwise;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.core.Response;
import java.net.URI;

/** Landing fallback after OIDC has authenticated the callback request. */
@Path("/oidc/callback")
public class OidcLandingResource {
  @GET
  @org.eclipse.microprofile.openapi.annotations.Operation(hidden = true)
  public Response landing() {
    // Authentication is enforced by the HTTP permission for this path.
    // A fixed target also removes authorization parameters from the browser URL.
    return Response.seeOther(URI.create("/")).build();
  }
}
