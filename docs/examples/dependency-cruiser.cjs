module.exports = {
  forbidden: [
    {
      name: "core-to-ui",
      severity: "error",
      from: { path: "^src/core/" },
      to: { path: "^src/ui/" },
    },
    {
      name: "no-unresolved-local-dependencies",
      severity: "error",
      from: { path: "^src/" },
      to: { couldNotResolve: true },
    },
    {
      name: "no-source-cycles",
      severity: "error",
      from: { path: "^src/" },
      to: { path: "^src/", circular: true },
    },
  ],
  options: { doNotFollow: { path: "node_modules" } },
};
