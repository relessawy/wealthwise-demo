package com.wealthwise.ui;

import io.vertx.ext.web.Router;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import java.util.function.Predicate;
import java.util.regex.Pattern;

@ApplicationScoped
public class SPARouting {

  private static final Predicate<String> FILE_NAME_PREDICATE =
      Pattern.compile(".+\\.[a-zA-Z0-9]+$").asMatchPredicate();

  public void init(@Observes Router router) {
    router
        .get("/*")
        .handler(
            rc -> {
              final String path = rc.normalizedPath();
              if (!path.startsWith("/api/")
                  && !path.startsWith("/q/")
                  && !path.equals("/")
                  && !FILE_NAME_PREDICATE.test(path)) {
                rc.reroute("/");
              } else {
                rc.next();
              }
            });
  }
}
