# Write Reproducible Test Cases

Write test cases from tested user actions.

## Use

Load `SKILL.md` in an agent with local skill support:

> Read requirements.md and tests/manual/. Examine the supplied application.
> Examine automated tests in the supplied repository. Save local cases and evidence.
> Do not change external systems.

The agent gets missing project details from the user.
An earlier suitable report can replace a new run.

Provide a browser tool. [Playwright CLI](https://github.com/microsoft/playwright-cli) supports actions, screenshots, traces, and network mocks.
See the [example](references/playwright-cli.md). The skill has no browser installer or TMS client.

The helper uses Python 3.10+ and the standard library. See [output](references/output.md).
Run its tests with synthetic data:

```bash
python3 -m unittest discover -s tests -v
```

These tests examine the helper, not browser execution or case quality.

Terms: *case*: test procedure; *mock*: replacement response; *repository*: code store; *artifact*: evidence file; *TMS*: test management system.
