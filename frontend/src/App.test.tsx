import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

vi.mock("./keycloak", () => ({
  default: {
    init: vi.fn().mockResolvedValue(true),
    tokenParsed: {
      preferred_username: "testuser",
      realm_access: { roles: ["user"] },
    },
    token: "fake-token",
    onTokenExpired: null,
    logout: vi.fn(),
    updateToken: vi.fn().mockResolvedValue(true),
  },
}));

import App from "./App";

test("renders Hello World when authenticated", async () => {
  render(<App />);
  const heading = await screen.findByText("Hello World");
  expect(heading).toBeInTheDocument();
});

test("displays username when authenticated", async () => {
  render(<App />);
  const username = await screen.findByText(/testuser/);
  expect(username).toBeInTheDocument();
});
