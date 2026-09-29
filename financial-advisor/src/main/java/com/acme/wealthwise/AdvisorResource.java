package com.acme.wealthwise;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import java.util.Map;
import java.util.UUID;

@Path("/chat")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class AdvisorResource {
  @Inject ObjectMapper mapper;

  public record Input(String message, String requestId) {}

  @POST
  public Map<String, String> chat(Input input, @HeaderParam("X-Demo-User") String user)
      throws Exception {
    user = Remote.user(user);
    if (input == null
        || input.message() == null
        || input.message().isBlank()
        || input.message().length() > 2000)
      throw new BadRequestException("A message of 1–2000 characters is required");
    String id = input.requestId();
    try {
      UUID.fromString(id);
    } catch (Exception e) {
      throw new BadRequestException("A UUID requestId is required");
    }
    String answer = DemoAdvice.answer(input.message());
    Remote.call(
        Remote.env("HISTORY_URL", "http://advisor-history:8080") + "/history",
        "POST",
        mapper.writeValueAsString(
            Map.of(
                "requestId",
                id,
                "kind",
                "financial",
                "question",
                input.message(),
                "answer",
                answer)),
        user);
    return Map.of("message", answer, "mode", "demonstration", "requestId", id);
  }
}
