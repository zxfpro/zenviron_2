import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { App } from "../../apps/frontend/src/App";

vi.mock("../../apps/frontend/src/services/configApi", () => ({
  fetchConfig: vi.fn(async () => ({
    version_hash: "hash",
    config: {
      meta: { version: 1, updated_at: "2026-03-25T00:00:00+00:00", active_alias: "openai_default" },
      profiles: {
        openai_default: {
          provider: "openai",
          enabled: true,
          base_url: "https://api.openai.com/v1",
          api_key: "",
          alias: "openai_default",
          model: "gpt-4o-mini",
          timeout: 30,
          max_tokens: 2048,
          temperature: 0.7,
          note: "",
        },
      },
    },
  })),
  patchProfile: vi.fn(),
  setActiveAlias: vi.fn(),
  subscribeConfigEvents: vi.fn(() => () => {}),
  testProfile: vi.fn(async () => ({ success: true, message: "ok" })),
}));

test("renders app shell", async () => {
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  );

  expect(await screen.findByText("Sentinel Archive")).toBeInTheDocument();
});
