import fs from "node:fs";

/** Private filesystem identities must survive JSON without rounding. */
export function isFileIdentityComponent(value) {
  return (Number.isSafeInteger(value) && value >= 0)
    || (typeof value === "string" && /^(0|[1-9][0-9]{0,38})$/.test(value)
      && BigInt(value) < (1n << 128n));
}

function component(value) {
  return value <= BigInt(Number.MAX_SAFE_INTEGER) ? Number(value) : value.toString();
}

function identityStat(stat) {
  // Preserve BigIntStats' native type predicates and derive every field from
  // the same observation, avoiding a second pathname lookup.
  return Object.assign(Object.create(stat), {
    dev: component(stat.dev), ino: component(stat.ino), size: Number(stat.size),
    mtimeMs: Number(stat.mtimeNs) / 1e6, ctimeMs: Number(stat.ctimeNs) / 1e6,
  });
}

export const lstatFileIdentity = (path) => identityStat(fs.lstatSync(path, {bigint: true}));
export const fstatFileIdentity = (descriptor) => identityStat(fs.fstatSync(descriptor, {bigint: true}));
