package com.acme.wealthwise;

import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import java.util.*;
import javax.sql.DataSource;

@Path("/history")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class HistoryResource {
  @Inject DataSource db;

  public record Entry(String requestId, String kind, String question, String answer) {}

  static String owner(String u) {
    if (u == null || !u.matches("[A-Za-z0-9._-]{1,64}"))
      throw new NotAuthorizedException("Demo identity required");
    return u;
  }

  @POST
  public Map<String, String> add(Entry e, @HeaderParam("X-Demo-User") String u) throws Exception {
    u = owner(u);
    if (e == null
        || !Set.of("financial", "investment").contains(e.kind() == null ? "" : e.kind())
        || e.question() == null
        || e.question().isBlank()
        || e.question().length() > 2000
        || e.answer() == null
        || e.answer().length() > 8000) throw new BadRequestException("Invalid history entry");
    UUID id;
    try {
      id = UUID.fromString(e.requestId());
    } catch (Exception x) {
      throw new BadRequestException("Invalid requestId");
    }
    try (var c = db.getConnection();
        var s =
            c.prepareStatement(
                "INSERT INTO history(request_id,owner,kind,question,answer) VALUES(?,?,?,?,?) ON"
                    + " CONFLICT(owner,request_id) DO NOTHING")) {
      s.setObject(1, id);
      s.setString(2, u);
      s.setString(3, e.kind());
      s.setString(4, e.question());
      s.setString(5, e.answer());
      int inserted = s.executeUpdate();
      if (inserted == 0)
        try (var existing =
            c.prepareStatement(
                "SELECT kind,question,answer FROM history WHERE owner=? AND request_id=?")) {
          existing.setString(1, u);
          existing.setObject(2, id);
          try (var rs = existing.executeQuery()) {
            if (!rs.next()
                || !e.kind().equals(rs.getString(1))
                || !e.question().equals(rs.getString(2))
                || !e.answer().equals(rs.getString(3)))
              throw new WebApplicationException(
                  "requestId already used for a different request", 409);
          }
        }
    }
    return Map.of("message", "saved", "requestId", id.toString());
  }

  @GET
  public Map<String, Object> list(
      @HeaderParam("X-Demo-User") String u,
      @QueryParam("limit") @DefaultValue("50") int limit,
      @QueryParam("offset") @DefaultValue("0") int offset)
      throws Exception {
    u = owner(u);
    if (limit < 1 || limit > 100 || offset < 0) throw new BadRequestException("Invalid pagination");
    var rows = new ArrayList<Map<String, Object>>();
    try (var c = db.getConnection();
        var s =
            c.prepareStatement(
                "SELECT id,request_id,kind,question,answer,created_at FROM history WHERE owner=?"
                    + " ORDER BY created_at DESC,id DESC LIMIT ? OFFSET ?")) {
      s.setString(1, u);
      s.setInt(2, limit);
      s.setInt(3, offset);
      try (var rs = s.executeQuery()) {
        while (rs.next()) {
          rows.add(
              Map.of(
                  "id",
                  rs.getLong(1),
                  "requestId",
                  rs.getString(2),
                  "kind",
                  rs.getString(3),
                  "question",
                  rs.getString(4),
                  "answer",
                  rs.getString(5),
                  "timestamp",
                  rs.getTimestamp(6).toInstant().toString()));
        }
      }
    }
    return Map.of("message", rows, "limit", limit, "offset", offset);
  }
}
