package com.acme.wealthwise;

import jakarta.ws.rs.*;
import jakarta.ws.rs.core.*;

@org.eclipse.microprofile.openapi.annotations.security.SecurityScheme(
    securitySchemeName = "demo",
    type = org.eclipse.microprofile.openapi.annotations.enums.SecuritySchemeType.HTTP,
    scheme = "basic")
@org.eclipse.microprofile.openapi.annotations.security.SecurityRequirement(name = "demo")
@Path("/api")
@Produces(MediaType.APPLICATION_JSON)
public class ApiResource {
  @GET
  @Path("/session")
  public Response session() {
    return Response.seeOther(java.net.URI.create("/")).build();
  }

  @POST
  @Path("/financial/chat")
  @Consumes(MediaType.APPLICATION_JSON)
  public String financial(String body, @Context SecurityContext ctx) {
    return Remote.call(
        Remote.env("FINANCIAL_URL", "http://financial-advisor:8080") + "/chat",
        "POST",
        body,
        ctx.getUserPrincipal().getName());
  }

  @POST
  @Path("/investment/chat")
  @Consumes(MediaType.APPLICATION_JSON)
  public String investment(String body, @Context SecurityContext ctx) {
    return Remote.call(
        Remote.env("INVESTMENT_URL", "http://investment-advisor:8080") + "/chat",
        "POST",
        body,
        ctx.getUserPrincipal().getName());
  }

  @GET
  @Path("/history")
  public String history(
      @Context SecurityContext ctx,
      @QueryParam("limit") @DefaultValue("50") int limit,
      @QueryParam("offset") @DefaultValue("0") int offset) {
    if (limit < 1 || limit > 100 || offset < 0) throw new BadRequestException("Invalid pagination");
    return Remote.call(
        Remote.env("HISTORY_URL", "http://advisor-history:8080")
            + "/history?limit="
            + limit
            + "&offset="
            + offset,
        "GET",
        null,
        ctx.getUserPrincipal().getName());
  }
}
