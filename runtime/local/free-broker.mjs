import {spawn, execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {setTimeout as delay} from 'node:timers/promises';
const execute = promisify(execFile);

/** Start only a missing local Free broker; never take ownership of an existing one. */
export async function ensureFreeBroker({python, script, env = process.env, timeoutMs = 10_000}) {
  const probe = async () => {
    const {stdout} = await execute(python, [script, 'status'], {env, timeout: 3000, maxBuffer: 1024 * 1024});
    return JSON.parse(stdout);
  };
  const existing = await probe();
  if (existing.error_code === 'EMBEDDED_BRIDGE_AUTH_FAILED') {
    throw new Error('An existing Free broker rejected authentication. Stop or repair that broker before retrying.');
  }
  if (existing.running === true) return {owned: false, close: async () => {}};
  const child = spawn(python, [script, 'serve'], {env, stdio: ['ignore', 'ignore', 'pipe']});
  let spawnError;
  child.on('error', error => { spawnError = error; });
  child.stderr.resume();
  let closed = false;
  const close = async () => {
    if (closed) return;
    closed = true;
    if (child.exitCode !== null || child.signalCode !== null) return;
    const exited = new Promise(resolve => child.once('exit', resolve));
    child.kill('SIGTERM');
    await Promise.race([exited, delay(3000)]);
    if (child.exitCode === null && child.signalCode === null) {
      child.kill('SIGKILL');
      await Promise.race([exited, delay(1000)]);
    }
  };
  try {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      if (spawnError) throw spawnError;
      if (child.exitCode !== null || child.signalCode !== null) throw new Error('The Free broker stopped during startup.');
      const status = await probe();
      if (status.running === true && !status.error_code) return {owned: true, close};
      await delay(100);
    }
    throw new Error('The Free broker did not become ready before the startup deadline.');
  } catch (error) {
    await close();
    throw error;
  }
}
