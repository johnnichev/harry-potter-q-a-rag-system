import { ask } from "../../../lib/api/client";

test("ask returns text", async () => {
  const m = vi
    .spyOn(globalThis, "fetch")
    .mockResolvedValue(new Response("ok", { status: 200 }));
  const res = await ask("q");
  expect(res).toBe("ok");
  m.mockRestore();
});

test("ask throws on error", async () => {
  const m = vi
    .spyOn(globalThis, "fetch")
    .mockResolvedValue(new Response("bad", { status: 500 }));
  await expect(ask("q")).rejects.toThrow("bad");
  m.mockRestore();
});
