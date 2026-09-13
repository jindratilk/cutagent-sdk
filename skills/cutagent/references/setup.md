# Set up CutAgent authoring

Read this for a first standalone SDK run, a first CutAgent-managed SDK script, or a connection failure. Continue to [SDK authoring](sdk.md) for the object model and exact editing methods, or [CutAgent CLI](cli.md) for direct commands.

Keep the SDK and CutAgent runtime version-matched. A successful import does not prove that the runtime can reach the intended DaVinci Resolve project.

## Set up the standalone public package

The current standalone source preview supports macOS and DaVinci Resolve 21.1 or later, Free or Studio. It requires:

- Node.js 22.12 or later on the Node 22 line, or Node.js 24.x
- Python 3.12
- FFmpeg and FFprobe on `PATH` for workflows that inspect or render media

Windows setup is not currently qualified. Check the installed `compatibility.json` and release status instead of assuming another platform or version works.

Build a reviewed source checkout and install its packed artifact into a clean consumer project:

```sh
git clone https://github.com/jindratilk/cutagent-sdk.git
cd cutagent-sdk
npm ci --ignore-scripts
npm run build
npm test
npm run test:types
npm run verify:source
npm pack --json

mkdir ../my-video-project
cd ../my-video-project
npm init -y
npm install /absolute/path/to/cutagent-3.0.0.tgz
```

Package setup may contact the configured npm and Python package indexes.

### DaVinci Resolve Studio

In **DaVinci Resolve > Preferences > System > General**, set **External scripting** to **Local**. Then install and start the standalone runtime:

```sh
npx cutagent setup
cutagent runtime start --transport studio_external
```

### DaVinci Resolve Free

Install the independent embedded utility during setup:

```sh
npx cutagent setup --free
```

In DaVinci Resolve, run **Workspace > Scripts > CutAgentSDK**, then start the runtime:

```sh
cutagent runtime start --transport embedded_free
```

Keep the runtime terminal open. It prints the discovery-file path used by SDK clients. When the client runs outside that shell environment, pass the absolute path to it:

```sh
export CUTAGENT_SDK_DISCOVERY_FILE=/absolute/path/to/cutagent-sdk-discovery-v1.json
```

Do not publish or persist the discovery file or its credentials. Do not enable network scripting for a local connection.

If setup reports `CUTAGENT_COMMAND_COLLISION`, it has preserved an existing `cutagent` command. Keep that command or install the standalone launcher into a separate directory:

```sh
npx cutagent setup --bin-dir "$HOME/.local/cutagent-sdk-bin"
```

Add that directory to `PATH` only for the shell that should use this installation.

## Verify a standalone connection

The package is Node.js ESM; browser and CommonJS entrypoints are not supported. Create `inspect-current-timeline.mjs` in the consumer project:

```js
import {CutAgent} from "cutagent";

const client = await CutAgent.connect({timeoutMs: 15_000});

try {
  const project = await client.projects.current({timeoutMs: 10_000});
  const timeline = await project.timelines.current({timeoutMs: 10_000});
  const snapshot = await timeline.snapshot({timeoutMs: 15_000});

  console.log(JSON.stringify({
    project: {id: project.id, name: project.name},
    timeline: {id: timeline.id, name: timeline.name},
    revision: snapshot.revision,
    frameRate: snapshot.frameRate.toString(),
    trackCount: snapshot.tracks.length,
  }, null, 2));
} finally {
  await client.close({timeoutMs: 10_000});
}
```

Run the read-only smoke check:

```sh
node inspect-current-timeline.mjs
```

If this resolves the wrong project or timeline, make the intended objects current in DaVinci Resolve and inspect again before authoring any mutation.

Inspect the managed installation with `cutagent status --json`. Updates are deliberate: install a reviewed newer artifact and rerun `npx cutagent setup`. `cutagent update` does not download or replace anything automatically.

## Use the managed runner inside CutAgent

Inside a CutAgent task, do not install the standalone package into the task workspace. The app supplies a compatible SDK, runtime discovery, Node.js executable, and `cutagent-sdk` runner.

The runner requires a current project and timeline. It connects once, captures one starting snapshot, imports the `.mjs` module, and supplies `{sdk, client, project, timeline, snapshot, progress}`. It closes the client after the module returns or throws.

Create a read-only runner script:

```js
export default async function inspectCurrentTimeline({
  client,
  project,
  timeline,
  snapshot,
  progress,
}) {
  progress("Reading the current timeline");

  console.log(JSON.stringify({
    connectionId: client.connection.connectionId,
    runtime: client.connection.descriptor.distribution,
    project: {id: project.id, name: project.name},
    timeline: {
      id: timeline.id,
      name: timeline.name,
      revision: snapshot.revision,
      trackCount: snapshot.tracks.length,
    },
  }, null, 2));
}
```

Run it with a short user-facing activity title and an absolute path:

```sh
cutagent-sdk --title "Inspect current timeline" /absolute/path/inspect-current-timeline.mjs
```

The title must be 1–200 characters; progress messages must be 1–500 characters. Both reject control characters. Reuse the supplied snapshot for the initial decision instead of opening another client or immediately repeating the same inspection. After a successful mutation, obtain fresh state before the next dependent change.

If `cutagent-sdk` is not on `PATH`, invoke the bundled runner paths already exposed to the task:

```sh
"${CUTAGENT_NODE_EXECUTABLE}" "${CUTAGENT_SDK_RUNNER_FILE}" \
  --title "Inspect current timeline" \
  /absolute/path/inspect-current-timeline.mjs
```

Use native environment-variable syntax in PowerShell. If either variable is missing, update or repair CutAgent rather than guessing installation paths.

Progress output and process exit describe runner activity; they are not generic proof that an edit is correct. Inspect the returned SDK operation and perform the domain-appropriate readback in [checking results](checking-results.md). If a long-running command yields, continue the same terminal process instead of starting a second runner.

## Recover connection failures

Branch on the structured error code:

- `RUNTIME_UNAVAILABLE`: start or restart the compatible runtime. Confirm that DaVinci Resolve is fully loaded and, for Free, that **Workspace > Scripts > CutAgentSDK** is running.
- `SDK_INCOMPATIBLE`: install the SDK/runtime combination named by the compatibility guidance; do not force the connection.
- `AUTHENTICATION_REQUIRED` or `SUBSCRIPTION_REQUIRED`: complete the requested action in the CutAgent app. These managed-product errors do not apply to ordinary local standalone editing.
- `CANCELLED`: the client request was aborted; this does not prove cancellation of an already-started operation.

After reconnecting, resolve the project, timeline, snapshot, and mutation targets again. If an error includes an operation ID or possible mutation state, inspect that original operation before retrying. Continue with [errors and recovery](errors-and-recovery.md).
