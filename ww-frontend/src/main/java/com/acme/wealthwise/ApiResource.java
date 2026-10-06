package com.acme.wealthwise;

import jakarta.ws.rs.*;
import jakarta.ws.rs.core.*;

@org.eclipse.microprofile.openapi.annotations.security.SecurityScheme(
    securitySchemeName = "oidc",
    type = org.eclipse.microprofile.openapi.annotations.enums.SecuritySchemeType.HTTP,
    scheme = "bearer", bearerFormat = "JWT")
@org.eclipse.microprofile.openapi.annotations.security.SecurityRequirement(name = "oidc")
@Path("/api")
@Produces(MediaType.APPLICATION_JSON)
public class ApiResource {
  @jakarta.inject.Inject org.eclipse.microprofile.jwt.JsonWebToken token;

  private String owner() {
    return HistoryIdentity.key(token.getIssuer(), token.getSubject());
  }

  @GET
  @Path("/me")
  public java.util.Map<String,String> me() {
    return java.util.Map.of("username", token.getClaim("preferred_username"), "identity", owner());
  }

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
        owner());
  }

  @POST
  @Path("/investment/chat")
  @Consumes(MediaType.APPLICATION_JSON)
  public String investment(String body, @Context SecurityContext ctx) {
    return Remote.call(
        Remote.env("INVESTMENT_URL", "http://investment-advisor:8080") + "/chat",
        "POST",
        body,
        owner());
  }

  @GET
  @Path("/savings-guidance")
  @org.eclipse.microprofile.openapi.annotations.Operation(
      summary = "Calculate a savings contribution",
      description = "Training calculator returning a monthly amount and general savings guidance. Uses the signed-in session or a bearer token.")
  public SavingsGuidance.Result savings(
      @QueryParam("target") @DefaultValue("1200.00") java.math.BigDecimal target,
      @QueryParam("saved") @DefaultValue("300.00") java.math.BigDecimal saved,
      @QueryParam("months") @DefaultValue("6") int months) {
    return SavingsGuidance.calculate(target, saved, months);
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
        owner());
  }
}
