// Reviewed release policy. Kept outside the wire-schema digest so a package
// patch does not create protocol drift when the wire contract is unchanged.
export const CUTAGENT_SDK_PREVIEW_VERSION = "0.2.0";
export const CUTAGENT_SDK_SUPPORTED_PACKAGE_MAJOR = 0;
export const CUTAGENT_SDK_SUPPORTED_PACKAGE_MINOR = 2;
export const CUTAGENT_SDK_RUNTIME_MIN_VERSION = "3.0.0";
export const CUTAGENT_SDK_RUNTIME_MAX_EXCLUSIVE_VERSION = "3.1.0";
const supportedRuntimeRange = `>=${CUTAGENT_SDK_RUNTIME_MIN_VERSION} <${CUTAGENT_SDK_RUNTIME_MAX_EXCLUSIVE_VERSION}`;
const publishedRuntimePolicy = Object.freeze({
    runtimeRange: supportedRuntimeRange,
    desktopManagedRange: supportedRuntimeRange,
    pluginManagedRange: null,
    cliRange: supportedRuntimeRange,
});
const numericIdentifier = "(?:0|[1-9]\\d*)";
const releaseVersionPattern = new RegExp(`^${numericIdentifier}\\.${numericIdentifier}\\.${numericIdentifier}$`);
const compatibleVersionPattern = new RegExp(`^(${numericIdentifier})\\.(${numericIdentifier})\\.(${numericIdentifier})`
    + "(?:-beta\\.[1-9]\\d*)?$");
const versionRangePattern = new RegExp(`^>=${numericIdentifier}\\.${numericIdentifier}\\.${numericIdentifier}(?:\\s+<${numericIdentifier}\\.${numericIdentifier}\\.${numericIdentifier})?$`);
function parseCompatibleVersionCore(input) {
    const match = compatibleVersionPattern.exec(input);
    if (!match)
        return null;
    try {
        return [BigInt(match[1]), BigInt(match[2]), BigInt(match[3])];
    }
    catch {
        return null;
    }
}
function parseReleaseVersion(input) {
    return releaseVersionPattern.test(input) ? parseCompatibleVersionCore(input) : null;
}
function compareVersions(left, right) {
    for (let index = 0; index < left.length; index += 1) {
        if (left[index] < right[index])
            return -1;
        if (left[index] > right[index])
            return 1;
    }
    return 0;
}
function satisfiesRange(input, range) {
    // Runtime policy is release-line based: the reviewed beta.N form belongs to
    // its stable core line, while every other prerelease form still fails closed.
    const parsed = parseCompatibleVersionCore(input);
    if (!parsed || !versionRangePattern.test(range))
        return false;
    const [minimumClause, maximumClause] = range.split(/\s+/);
    if (!minimumClause?.startsWith(">="))
        return false;
    const minimum = parseReleaseVersion(minimumClause.slice(2));
    const maximum = maximumClause?.startsWith("<")
        ? parseReleaseVersion(maximumClause.slice(1))
        : null;
    if (!minimum || compareVersions(parsed, minimum) < 0)
        return false;
    if (maximumClause !== undefined && maximum === null)
        return false;
    return maximum === null || compareVersions(parsed, maximum) < 0;
}
/** Evaluate the independently versioned runtime, distribution, and CutAgent CLI axes. */
export function evaluateCutAgentSdkRuntimeCompatibility(input, policy = publishedRuntimePolicy) {
    const issues = [];
    if (!satisfiesRange(input.runtimeVersion, policy.runtimeRange)) {
        issues.push({
            axis: "runtime",
            received: input.runtimeVersion,
            supported: policy.runtimeRange,
        });
    }
    const distributionRange = input.distribution === "standalone_local"
        ? policy.desktopManagedRange
        : policy.pluginManagedRange;
    if (policy.expectedDistribution !== undefined && input.distribution !== policy.expectedDistribution) {
        issues.push({
            axis: "distribution",
            received: input.distribution,
            supported: policy.expectedDistribution,
        });
    }
    if (distributionRange === null || !satisfiesRange(input.distributionVersion, distributionRange)) {
        issues.push({
            axis: "distribution",
            received: `${input.distribution}:${input.distributionVersion}`,
            supported: distributionRange ?? "standalone_local only",
        });
    }
    if (!satisfiesRange(input.cliVersion, policy.cliRange)) {
        issues.push({
            axis: "cli",
            received: input.cliVersion,
            supported: policy.cliRange,
        });
    }
    return issues.length === 0 ? { compatible: true } : { compatible: false, issues };
}
