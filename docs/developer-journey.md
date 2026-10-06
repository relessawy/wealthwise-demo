# WW-1: from request to a visible improvement

Alice wants customers to see an actionable monthly savings message instead of
vague guidance. Keep Jira WW-1 open until the deployed application and Docs prove
the improvement.

## Before editing

1. Open WealthWise's Jira tab in Developer Hub. Move WW-1 to **In Progress**.
2. Launch its Dev Spaces workspace. Confirm the repository, branch and clean
   working tree using `git status`; retain any participant work.
3. Run `mvn -B -ntp verify`. In the running application, calculate the default goal
   and observe the generic guidance with a monthly amount of 150.00.

## Make one coherent change

In `ww-frontend/src/main/java/com/acme/wealthwise/SavingsGuidance.java`, replace
only the body of `guidance`:

```java
if (monthly.signum() == 0) return "Your savings goal is already reached.";
return "Save " + monthly.toPlainString() + " per month for " + months + " months to reach your goal.";
```

In `SavingsGuidanceTest.java`, change the sample guidance assertion to:

```java
assertEquals("Save 150.00 per month for 6 months to reach your goal.", result.guidance());
```

Add a check for the reached-goal message. In `ApiResource.java`, change the OpenAPI
operation description from general guidance to **actionable monthly savings
guidance**. In `docs/savings-api.md`, replace the current guidance sentence with
**Save 150.00 per month for 6 months to reach your goal.**

Run the tests again and review `git diff`. Commit the Java change, tests, API
contract and documentation together:

```bash
git add ww-frontend/src/main/java/com/acme/wealthwise/SavingsGuidance.java \
  ww-frontend/src/main/java/com/acme/wealthwise/ApiResource.java \
  ww-frontend/src/test/java/com/acme/wealthwise/SavingsGuidanceTest.java \
  docs/savings-api.md
git commit -m "WW-1 Provide actionable monthly savings guidance"
git push origin main
```

The issue key in the commit message provides traceability. The Bitbucket push
webhook triggers Jenkins; changing Jira status does not trigger a build.

## Verify before Done

- In Developer Hub **CI**, observe the tests, security gates and delivery stages.
- Check that the deployed digest and published Docs correspond to that commit.
- In WealthWise **Savings goal**, calculate 1200.00 / 300.00 / 6 and see
  **Save 150.00 per month for 6 months to reach your goal.**
- In Swagger UI execute the same request and confirm that `guidance` matches.
- In Developer Hub **Docs**, read the updated Savings API page.
- Only after those checks, move WW-1 to **Done** in the Jira tab.

## Repeat without losing work

Record the exercise commit SHA. If this is your disposable rehearsal repository,
review `git status` and use `git revert <exercise-commit-sha>` followed by a normal
push to restore the baseline through the same pipeline. Never force-push or reset
another participant's changes. Use a fresh participant repository when histories
differ or a revert would conflict.
