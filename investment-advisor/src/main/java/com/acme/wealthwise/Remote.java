package com.acme.wealthwise;

import jakarta.ws.rs.*;
import java.net.URI;
import java.net.http.*;
import java.time.Duration;

public final class Remote {
  private static final HttpClient CLIENT =
      HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build();

  public static String call(String url, String method, String body, String user) {
    try {
      var b =
          HttpRequest.newBuilder(URI.create(url))
              .timeout(Duration.ofSeconds(8))
              .header("Content-Type", "application/json")
              .header("X-Demo-User", user);
      b.method(
          method,
          body == null
              ? HttpRequest.BodyPublishers.noBody()
              : HttpRequest.BodyPublishers.ofString(body));
      var r = CLIENT.send(b.build(), HttpResponse.BodyHandlers.ofString());
      if (r.statusCode() < 200 || r.statusCode() > 299)
        throw new WebApplicationException(
            "Dependency rejected request", r.statusCode() < 500 ? r.statusCode() : 502);
      return r.body();
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
      throw new WebApplicationException("Request interrupted", 503);
    } catch (WebApplicationException e) {
      throw e;
    } catch (Exception e) {
      throw new WebApplicationException("Dependency unavailable", 503);
    }
  }

  public static String env(String key, String fallback) {
    return System.getenv().getOrDefault(key, fallback);
  }

  public static String user(String user) {
    if (user == null || !user.matches("[A-Za-z0-9._-]{1,64}"))
      throw new NotAuthorizedException("Demo identity required");
    return user;
  }
}
