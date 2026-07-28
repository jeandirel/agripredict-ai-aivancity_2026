import {
  type ChangeEvent,
  type FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { AnimatePresence, MotionConfig, motion, useReducedMotion } from "motion/react";
import {
  Activity,
  AlertTriangle,
  ArrowDown,
  ArrowRight,
  BarChart3,
  Braces,
  CalendarClock,
  Check,
  ChevronDown,
  CircleGauge,
  CloudSun,
  Database,
  Eye,
  Fingerprint,
  FlaskConical,
  Globe2,
  Languages,
  Layers3,
  Leaf,
  Orbit,
  Pause,
  Play,
  Radar,
  RefreshCw,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  Sprout,
  Telescope,
  ThermometerSun,
  Upload,
} from "lucide-react";
import { ApiError, loadObservatory, predictHarvest } from "./api";
import { ComparisonPlot, Constellation, SignalLoom, TruthLens } from "./components/Canvases";
import { getCopy, type Copy } from "./i18n";
import type {
  EvaluationProtocol,
  FeatureDescriptor,
  Horizon,
  Language,
  Modality,
  ObservatoryData,
  PredictionResponse,
} from "./types";
import {
  MODALITY_COLORS,
  activeModalities,
  coverageLevel,
  cutoffIso,
  dayDifference,
  displayValue,
  featureLabel,
  formatDate,
  formatNumber,
  formatPercent,
  horizonLabel,
  modalityCounts,
  normalizeModality,
  parseFeatureFile,
  rawValue,
  referenceValues,
  referenceYear,
} from "./utils";

type LoadState = "loading" | "ready" | "error";
type ProfileMode = "synthetic" | "custom" | "expert";

const ACT_IDS = ["fusion", "forecast", "duel", "evidence", "oversight"] as const;

const modalityIcons: Record<Modality, typeof Sprout> = {
  soil: Sprout,
  sentinel1: Radar,
  sentinel2: Eye,
  weather: CloudSun,
  context: Layers3,
  other: Database,
};

function useActiveAct() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const onScroll = () => {
      const marker = window.scrollY + window.innerHeight * 0.42;
      let current = 0;
      ACT_IDS.forEach((id, index) => {
        const element = document.getElementById(id);
        if (element && element.offsetTop <= marker) current = index;
      });
      setActive(current);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return active;
}

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function resolveTargetNature(data: ObservatoryData): string | undefined {
  if (data.overview.target_nature) return data.overview.target_nature;
  const { target } = data.overview;
  if (typeof target === "string") return target;
  return target?.nature ?? target?.notice ?? target?.name;
}

function protocolFrom(data: ObservatoryData): EvaluationProtocol {
  return data.overview.protocol ?? {};
}

function App() {
  const [language, setLanguage] = useState<Language>("fr");
  const [horizon, setHorizon] = useState<Horizon>("may31");
  const [paused, setPaused] = useState(false);
  const [state, setState] = useState<LoadState>("loading");
  const [data, setData] = useState<ObservatoryData | null>(null);
  const [loadError, setLoadError] = useState<string>("");
  const reducedMotion = useReducedMotion();
  const activeAct = useActiveAct();
  const copy = getCopy(language);

  const load = useCallback(async () => {
    setState("loading");
    setLoadError("");
    try {
      const next = await loadObservatory();
      setData(next);
      setState("ready");
    } catch (error) {
      setData(null);
      setLoadError(error instanceof Error ? error.message : "API unavailable");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    document.documentElement.lang = language;
    document.title =
      language === "fr"
        ? "AgriPredict — L’Observatoire de la Récolte"
        : "AgriPredict — The Harvest Observatory";
  }, [language]);

  const schema = data?.schemas[horizon];
  const counts = useMemo(
    () =>
      schema
        ? modalityCounts(schema.features)
        : { soil: 0, sentinel1: 0, sentinel2: 0, weather: 0, context: 0, other: 0 },
    [schema],
  );

  const labels: Record<Modality, string> = {
    soil: copy.soil,
    sentinel1: copy.sentinel1,
    sentinel2: copy.sentinel2,
    weather: copy.weather,
    context: copy.context,
    other: copy.other,
  };

  return (
    <MotionConfig reducedMotion="user" transition={{ duration: paused ? 0 : 0.55 }}>
      <div
        className={`observatory ${paused || reducedMotion ? "motion-paused" : ""}`}
        data-testid="observatory"
      >
        <a className="skip-link" href="#main">
          {copy.skip}
        </a>
        <TopBar
          language={language}
          setLanguage={setLanguage}
          paused={paused}
          setPaused={setPaused}
          state={state}
          modelCount={data?.health.available_models?.length}
          copy={copy}
        />
        <MissionRail active={activeAct} copy={copy} />

        <main id="main">
          <Hero
            state={state}
            modelCount={data?.health.available_models?.length}
            domain={data?.overview.domain}
            generatedAt={data?.overview.generated_at}
            copy={copy}
            language={language}
          />

          {state === "error" && (
            <OfflinePanel
              copy={copy}
              language={language}
              error={loadError}
              retry={() => void load()}
            />
          )}

          <section className="act act-fusion" id="fusion" aria-labelledby="fusion-title">
            <ActHeading
              number="01"
              kicker={copy.loomKicker}
              title={copy.loomTitle}
              body={copy.loomBody}
              id="fusion-title"
            />
            <div className="loom-shell">
              <div className="loom-toolbar">
                <div className="horizon-control" aria-label={copy.horizonSwitch}>
                  {(["may31", "june15"] as Horizon[]).map((item) => (
                    <button
                      type="button"
                      key={item}
                      className={item === horizon ? "active" : ""}
                      aria-pressed={item === horizon}
                      onClick={() => setHorizon(item)}
                    >
                      <span>{copy.observation}</span>
                      {horizonLabel(item, language)}
                    </button>
                  ))}
                </div>
                <div className="loom-total">
                  <Activity aria-hidden="true" />
                  <span>
                    {schema ? schema.user_feature_count : "—"} {copy.signals}
                  </span>
                </div>
              </div>
              {schema ? (
                <>
                  <SignalLoom
                    counts={counts}
                    horizon={horizon}
                    language={language}
                    paused={paused || Boolean(reducedMotion)}
                    labels={labels}
                  />
                  <div className="modality-legend">
                    {activeModalities(schema.features).map((modality) => {
                      const Icon = modalityIcons[modality];
                      return (
                        <div className="legend-item" key={modality}>
                          <span
                            className="legend-icon"
                            style={{ "--modality": MODALITY_COLORS[modality] } as React.CSSProperties}
                          >
                            <Icon aria-hidden="true" />
                          </span>
                          <span>
                            <strong>{labels[modality]}</strong>
                            <small>
                              {counts[modality]} {copy.signals}
                            </small>
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </>
              ) : (
                <DataUnavailable copy={copy} loading={state === "loading"} />
              )}
            </div>
            {reducedMotion && <p className="reduced-note">{copy.reduced}</p>}
          </section>

          <section className="act act-forecast" id="forecast" aria-labelledby="forecast-title">
            <ActHeading
              number="02"
              kicker={copy.forecastKicker}
              title={copy.forecastTitle}
              id="forecast-title"
            />
            {schema && data ? (
              <Predictor
                key={horizon}
                schema={schema}
                horizon={horizon}
                language={language}
                copy={copy}
                protocol={protocolFrom(data)}
              />
            ) : (
              <DataUnavailable copy={copy} loading={state === "loading"} />
            )}
          </section>

          <section className="act act-duel" id="duel" aria-labelledby="duel-title">
            <ActHeading
              number="03"
              kicker={copy.duelKicker}
              title={copy.duelTitle}
              id="duel-title"
            />
            {data ? (
              <HorizonDuel data={data} language={language} copy={copy} />
            ) : (
              <DataUnavailable copy={copy} loading={state === "loading"} />
            )}
          </section>

          <section className="act act-evidence" id="evidence" aria-labelledby="evidence-title">
            <ActHeading
              number="04"
              kicker={language === "fr" ? "Chambre des preuves" : "Evidence chamber"}
              title={copy.scientificProofs}
              id="evidence-title"
            />
            {data ? (
              <EvidenceChamber
                data={data}
                horizon={horizon}
                setHorizon={setHorizon}
                language={language}
                copy={copy}
              />
            ) : (
              <DataUnavailable copy={copy} loading={state === "loading"} />
            )}
          </section>

          <section className="act act-oversight" id="oversight" aria-labelledby="oversight-title">
            <ActHeading
              number="05"
              kicker={copy.trustGate}
              title={copy.trustTitle}
              id="oversight-title"
            />
            {data ? (
              <TrustGate data={data} language={language} copy={copy} />
            ) : (
              <DataUnavailable copy={copy} loading={state === "loading"} />
            )}
          </section>
        </main>

        <footer>
          <div className="footer-brand">
            <BrandMark />
            <div>
              <strong>AgriPredict</strong>
              <span>The Harvest Observatory</span>
            </div>
          </div>
          <p>{copy.oversight}</p>
          <button type="button" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
            {language === "fr" ? "Retour au ciel" : "Back to the sky"} <ArrowDown />
          </button>
        </footer>
      </div>
    </MotionConfig>
  );
}

interface TopBarProps {
  language: Language;
  setLanguage: (language: Language) => void;
  paused: boolean;
  setPaused: (paused: boolean) => void;
  state: LoadState;
  modelCount?: number;
  copy: Copy;
}

function TopBar({
  language,
  setLanguage,
  paused,
  setPaused,
  state,
  modelCount,
  copy,
}: TopBarProps) {
  return (
    <header className="topbar">
      <button className="brand-button" type="button" onClick={() => window.scrollTo({ top: 0 })}>
        <BrandMark />
        <span>
          <strong>AgriPredict</strong>
          <small>{copy.brandKicker}</small>
        </span>
      </button>
      <div className="topbar-actions">
        <div
          className={`service-status ${state === "ready" ? "online" : state}`}
          role="status"
          aria-live="polite"
        >
          <span className="status-pulse" />
          <span>{state === "ready" ? copy.online : copy.offline}</span>
          {state === "ready" && modelCount !== undefined && (
            <small>
              {modelCount} {copy.models}
            </small>
          )}
        </div>
        <button
          type="button"
          className="icon-button motion-toggle"
          onClick={() => setPaused(!paused)}
          aria-label={paused ? copy.resume : copy.pause}
          title={paused ? copy.resume : copy.pause}
        >
          {paused ? <Play aria-hidden="true" /> : <Pause aria-hidden="true" />}
        </button>
        <button
          type="button"
          className="language-toggle"
          onClick={() => setLanguage(language === "fr" ? "en" : "fr")}
          aria-label={language === "fr" ? "Switch to English" : "Passer en français"}
        >
          <Languages aria-hidden="true" />
          <span>{language.toUpperCase()}</span>
        </button>
      </div>
    </header>
  );
}

function BrandMark() {
  return (
    <span className="brand-mark" aria-hidden="true">
      <span />
      <span />
      <span />
    </span>
  );
}

function MissionRail({ active, copy }: { active: number; copy: Copy }) {
  return (
    <nav className="mission-rail" aria-label="Mission">
      <div className="rail-track" aria-hidden="true">
        <span style={{ height: `${(active / (ACT_IDS.length - 1)) * 100}%` }} />
      </div>
      {ACT_IDS.map((id, index) => (
        <button
          type="button"
          key={id}
          className={index === active ? "active" : ""}
          aria-current={index === active ? "step" : undefined}
          onClick={() => scrollTo(id)}
        >
          <span>{String(index + 1).padStart(2, "0")}</span>
          <em>{copy.acts[index]}</em>
        </button>
      ))}
    </nav>
  );
}

interface HeroProps {
  state: LoadState;
  modelCount?: number;
  domain?: string;
  generatedAt?: string;
  copy: Copy;
  language: Language;
}

function Hero({ state, modelCount, domain, generatedAt, copy, language }: HeroProps) {
  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="hero-atmosphere" aria-hidden="true">
        <div className="sun-disc" />
        <div className="orbit orbit-a" />
        <div className="orbit orbit-b" />
        <div className="grain-field">
          {Array.from({ length: 24 }).map((_, index) => (
            <i key={index} style={{ "--i": index } as React.CSSProperties} />
          ))}
        </div>
      </div>
      <div className="hero-content">
        <motion.p
          className="eyebrow"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Sparkles aria-hidden="true" />
          {copy.heroEyebrow}
        </motion.p>
        <motion.h1
          id="hero-title"
          initial={{ opacity: 0, y: 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.08 }}
        >
          <span>{copy.heroTitleA}</span>
          <em>{copy.heroTitleB}</em>
        </motion.h1>
        <motion.p
          className="hero-copy"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.16 }}
        >
          {copy.heroBody}
        </motion.p>
        <motion.div
          className="hero-actions"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.24 }}
        >
          <button type="button" className="primary-button" onClick={() => scrollTo("fusion")}>
            {copy.launch}
            <ArrowDown aria-hidden="true" />
          </button>
          <button type="button" className="text-button" onClick={() => scrollTo("evidence")}>
            {copy.explore}
            <ArrowRight aria-hidden="true" />
          </button>
        </motion.div>
      </div>
      <div className="hero-proof">
        <div className="hero-proof-label">
          <Telescope aria-hidden="true" />
          <span>{language === "fr" ? "État de l’observatoire" : "Observatory status"}</span>
        </div>
        <div className="hero-proof-grid">
          <div>
            <small>{state === "ready" ? copy.online : copy.offline}</small>
            <strong>{state === "ready" && modelCount !== undefined ? modelCount : "—"}</strong>
          </div>
          <div>
            <small>{language === "fr" ? "Domaine" : "Domain"}</small>
            <strong>{domain ?? "—"}</strong>
          </div>
          <div>
            <small>{copy.generated}</small>
            <strong>
              {generatedAt
                ? new Intl.DateTimeFormat(language, {
                    dateStyle: "medium",
                    timeStyle: "short",
                  }).format(new Date(generatedAt))
                : "—"}
            </strong>
          </div>
        </div>
      </div>
      <button className="hero-scroll" type="button" onClick={() => scrollTo("fusion")}>
        <span>{copy.act} 01</span>
        <ChevronDown aria-hidden="true" />
      </button>
    </section>
  );
}

function ActHeading({
  number,
  kicker,
  title,
  body,
  id,
}: {
  number: string;
  kicker: string;
  title: string;
  body?: string;
  id: string;
}) {
  return (
    <motion.header
      className="act-heading"
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.35 }}
    >
      <span className="act-number">{number}</span>
      <div>
        <p>{kicker}</p>
        <h2 id={id}>{title}</h2>
        {body && <div className="act-description">{body}</div>}
      </div>
    </motion.header>
  );
}

function DataUnavailable({ copy, loading }: { copy: Copy; loading: boolean }) {
  return (
    <div className={`data-unavailable ${loading ? "loading" : ""}`}>
      <div className="skeleton-orbit" aria-hidden="true" />
      <p>{loading ? "Synchronisation…" : copy.noData}</p>
    </div>
  );
}

function OfflinePanel({
  copy,
  language,
  error,
  retry,
}: {
  copy: Copy;
  language: Language;
  error: string;
  retry: () => void;
}) {
  return (
    <aside className="offline-panel" role="alert">
      <AlertTriangle aria-hidden="true" />
      <div>
        <strong>{copy.errorTitle}</strong>
        <p>{copy.noData}</p>
        <small>
          {new Intl.DateTimeFormat(language, {
            dateStyle: "medium",
            timeStyle: "medium",
          }).format(new Date())}{" "}
          · {error}
        </small>
      </div>
      <button type="button" onClick={retry}>
        <RefreshCw aria-hidden="true" /> {copy.retry}
      </button>
    </aside>
  );
}

interface PredictorProps {
  schema: ObservatoryData["schemas"][Horizon];
  horizon: Horizon;
  language: Language;
  copy: Copy;
  protocol: EvaluationProtocol;
}

function Predictor({ schema, horizon, language, copy, protocol }: PredictorProps) {
  const fallbackYear = protocol.test_year ?? new Date().getFullYear();
  const profileValues = useMemo(() => referenceValues(schema.reference_profile), [schema]);
  const [mode, setMode] = useState<ProfileMode>("synthetic");
  const [year, setYear] = useState(() =>
    referenceYear(schema.reference_profile, fallbackYear),
  );
  const [features, setFeatures] = useState<Record<string, unknown>>(profileValues);
  const [expertText, setExpertText] = useState(() =>
    JSON.stringify(profileValues, null, 2),
  );
  const [expertError, setExpertError] = useState("");
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [predictionError, setPredictionError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const visibleFields = useMemo(() => {
    const byModality = new Map<Modality, FeatureDescriptor[]>();
    for (const descriptor of schema.features.filter((item) => item.name !== "year")) {
      const modality = normalizeModality(descriptor.modality, descriptor.name);
      byModality.set(modality, [...(byModality.get(modality) ?? []), descriptor]);
    }
    const chosen: FeatureDescriptor[] = [];
    const preferred = [
      /SURF_PARC/i,
      /phh2o_0-5cm/i,
      /nitrogen_0-5cm/i,
      /s1_vv_mean/i,
      /s2_ndvi_may_mean/i,
      /meteo_gdd_(to_may31|amj)/i,
      /^region$/i,
    ];
    for (const pattern of preferred) {
      const match = schema.features.find((item) => pattern.test(item.name));
      if (match && !chosen.includes(match)) chosen.push(match);
    }
    for (const modality of ["soil", "sentinel1", "sentinel2", "weather", "context"] as Modality[]) {
      const candidate = byModality.get(modality)?.find((item) => !chosen.includes(item));
      if (candidate && chosen.length < 10) chosen.push(candidate);
    }
    return chosen.slice(0, 10);
  }, [schema.features]);

  const selectMode = (next: ProfileMode) => {
    setMode(next);
    setPrediction(null);
    setPredictionError("");
    setExpertError("");
    if (next === "synthetic") {
      setFeatures(profileValues);
      setExpertText(JSON.stringify(profileValues, null, 2));
      setYear(referenceYear(schema.reference_profile, fallbackYear));
    } else {
      setFeatures({});
      setExpertText("{}");
    }
  };

  const updateField = (descriptor: FeatureDescriptor, value: string) => {
    setFeatures((current) => {
      const next = { ...current };
      if (value === "") {
        delete next[descriptor.name];
      } else {
        const numeric = Number(value);
        const displayed = Number.isFinite(numeric) && value.trim() !== "" ? numeric : value;
        next[descriptor.name] = rawValue(descriptor, displayed);
      }
      return next;
    });
  };

  const onExpertChange = (value: string) => {
    setExpertText(value);
    try {
      const parsed = JSON.parse(value) as unknown;
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
        throw new Error(copy.invalidJson);
      }
      setFeatures(parsed as Record<string, unknown>);
      setExpertError("");
    } catch {
      setExpertError(copy.invalidJson);
    }
  };

  const importFile = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const parsed = parseFeatureFile(await file.text(), file.name);
      setFeatures(parsed);
      setExpertText(JSON.stringify(parsed, null, 2));
      setExpertError("");
    } catch {
      setExpertError(copy.invalidJson);
    } finally {
      event.target.value = "";
    }
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (expertError) return;
    setSubmitting(true);
    setPredictionError("");
    try {
      setPrediction(await predictHarvest(horizon, Number(year), features));
    } catch (error) {
      const detail = error instanceof ApiError ? error.detail || error.message : String(error);
      setPredictionError(detail);
      setPrediction(null);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="forecast-grid">
      <form className="profile-studio" onSubmit={(event) => void submit(event)}>
        <div className="mode-tabs" role="tablist" aria-label="Data profile">
          {(
            [
              ["synthetic", copy.synthetic, Fingerprint],
              ["custom", copy.custom, SlidersIcon],
              ["expert", copy.expert, Braces],
            ] as [ProfileMode, string, typeof Fingerprint][]
          ).map(([item, label, Icon]) => (
            <button
              type="button"
              role="tab"
              aria-selected={mode === item}
              className={mode === item ? "active" : ""}
              key={item}
              onClick={() => selectMode(item)}
            >
              <Icon aria-hidden="true" />
              {label}
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={mode}
            className="profile-body"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
          >
            <div className={`profile-notice ${mode}`}>
              {mode === "synthetic" ? <Fingerprint aria-hidden="true" /> : <ScanSearch aria-hidden="true" />}
              <div>
                <strong>{mode === "synthetic" ? copy.synthetic : copy.custom}</strong>
                <p>{mode === "synthetic" ? copy.syntheticNotice : copy.customNotice}</p>
              </div>
              {mode === "synthetic" && (
                <span className="complete-badge">
                  <Check aria-hidden="true" />
                  {schema.user_feature_count}/{schema.user_feature_count}
                </span>
              )}
            </div>

            <label className="year-field">
              <span>{copy.year}</span>
              <input
                type="number"
                min="2000"
                max="2100"
                value={year}
                onChange={(event) => setYear(Number(event.target.value))}
              />
            </label>

            {mode === "synthetic" && (
              <div className="profile-preview">
                {visibleFields.slice(0, 6).map((descriptor) => (
                  <div key={descriptor.name}>
                    <span
                      style={
                        {
                          "--feature-color":
                            MODALITY_COLORS[
                              normalizeModality(descriptor.modality, descriptor.name)
                            ],
                        } as React.CSSProperties
                      }
                    />
                    <small>{featureLabel(descriptor, language)}</small>
                    <strong>
                      {String(
                        displayValue(
                          descriptor,
                          profileValues[descriptor.name] ??
                            descriptor.reference_raw ??
                            descriptor.reference_value,
                        ) ?? "—",
                      )}
                      {descriptor.display_unit ? ` ${descriptor.display_unit}` : ""}
                    </strong>
                  </div>
                ))}
              </div>
            )}

            {mode === "custom" && (
              <div className="business-form">
                {visibleFields.map((descriptor) => {
                  const current = features[descriptor.name];
                  const value = displayValue(descriptor, current);
                  const isText =
                    typeof (descriptor.reference_raw ?? descriptor.reference_value) === "string" ||
                    descriptor.name.toLowerCase() === "region";
                  return (
                    <label key={descriptor.name}>
                      <span>{featureLabel(descriptor, language)}</span>
                      <div className="input-with-unit">
                        <input
                          type={isText ? "text" : "number"}
                          step="any"
                          value={value === undefined || value === null ? "" : String(value)}
                          onChange={(event) => updateField(descriptor, event.target.value)}
                          placeholder={
                            (descriptor.reference_raw ?? descriptor.reference_value) !== undefined
                              ? String(
                                  displayValue(
                                    descriptor,
                                    descriptor.reference_raw ?? descriptor.reference_value,
                                  ),
                                )
                              : undefined
                          }
                        />
                        {descriptor.display_unit && <em>{descriptor.display_unit}</em>}
                      </div>
                    </label>
                  );
                })}
              </div>
            )}

            {mode === "expert" && (
              <div className="expert-editor">
                <label className="file-button">
                  <Upload aria-hidden="true" />
                  {copy.import}
                  <input
                    type="file"
                    accept=".json,.csv,application/json,text/csv"
                    onChange={(event) => void importFile(event)}
                  />
                </label>
                <label>
                  <span className="sr-only">{copy.jsonPlaceholder}</span>
                  <textarea
                    value={expertText}
                    onChange={(event) => onExpertChange(event.target.value)}
                    spellCheck={false}
                    aria-invalid={Boolean(expertError)}
                    placeholder={copy.jsonPlaceholder}
                  />
                </label>
                {expertError && (
                  <p className="field-error" role="alert">
                    <AlertTriangle aria-hidden="true" /> {expertError}
                  </p>
                )}
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        <div className="profile-actions">
          <button className="primary-button" type="submit" disabled={submitting || Boolean(expertError)}>
            {submitting ? <RefreshCw className="spin" aria-hidden="true" /> : <CalendarClock aria-hidden="true" />}
            {submitting ? copy.calculating : copy.calculate}
          </button>
          <button type="button" className="reset-button" onClick={() => selectMode("synthetic")}>
            <RefreshCw aria-hidden="true" /> {copy.reset}
          </button>
        </div>
      </form>

      <Chronoscope
        prediction={prediction}
        error={predictionError}
        horizon={horizon}
        year={Number(year)}
        language={language}
        copy={copy}
        schema={schema}
      />
    </div>
  );
}

function SlidersIcon(props: React.ComponentProps<typeof CircleGauge>) {
  return <CircleGauge {...props} />;
}

interface ChronoscopeProps {
  prediction: PredictionResponse | null;
  error: string;
  horizon: Horizon;
  year: number;
  language: Language;
  copy: Copy;
  schema: ObservatoryData["schemas"][Horizon];
}

function Chronoscope({
  prediction,
  error,
  horizon,
  year,
  language,
  copy,
  schema,
}: ChronoscopeProps) {
  const interval = prediction?.prediction_interval_approx_90;
  const leadTime = prediction
    ? dayDifference(cutoffIso(horizon, year), prediction.predicted_date)
    : null;
  const evidence = prediction?.input_evidence;
  const coverage = prediction?.input_coverage;
  const level = coverageLevel(evidence, coverage);
  const supplied =
    evidence?.provided_user_features ??
    evidence?.supplied_user_features ??
    evidence?.supplied_feature_count;
  const expected = evidence?.expected_user_features ?? schema.user_feature_count;

  return (
    <div
      className={`chronoscope ${prediction ? "has-result" : ""}`}
      aria-live="polite"
      aria-busy={!prediction && !error ? undefined : false}
    >
      <div className="chronoscope-rings" aria-hidden="true">
        <i />
        <i />
        <i />
        <span />
      </div>
      {error ? (
        <div className="chronoscope-state error" role="alert">
          <AlertTriangle aria-hidden="true" />
          <strong>{copy.errorTitle}</strong>
          <p>{error}</p>
        </div>
      ) : !prediction ? (
        <div className="chronoscope-state">
          <Telescope aria-hidden="true" />
          <strong>{copy.predictionReady}</strong>
          <p>{copy.predictionEmpty}</p>
        </div>
      ) : (
        <motion.div
          className="chronoscope-result"
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <p>{copy.predictedDate}</p>
          <h3>{formatDate(prediction.predicted_date, language)}</h3>
          <span className={`coverage-chip ${level}`}>
            <span />
            {copy[level]}
          </span>
          <div className="interval-track" aria-label={copy.nominalInterval}>
            <span className="interval-line" />
            <i className="interval-low" />
            <i className="interval-center" />
            <i className="interval-high" />
          </div>
          <div className="interval-dates">
            <span>{formatDate(interval?.low_date, language)}</span>
            <small>
              {copy.nominalInterval}
              {interval?.nominal_coverage !== undefined
                ? ` · ${formatPercent(interval.nominal_coverage, language)}`
                : ""}
            </small>
            <span>{formatDate(interval?.high_date, language)}</span>
          </div>
          <div className="chronoscope-metrics">
            <div>
              <CalendarClock aria-hidden="true" />
              <span>
                <small>{copy.cutoff}</small>
                <strong>{formatDate(cutoffIso(horizon, year), language)}</strong>
              </span>
            </div>
            <div>
              <ThermometerSun aria-hidden="true" />
              <span>
                <small>{copy.leadTime}</small>
                <strong>
                  {leadTime !== null ? `${formatNumber(leadTime, language, 0)} ${copy.days}` : "—"}
                </strong>
              </span>
            </div>
            <div>
              <CircleGauge aria-hidden="true" />
              <span>
                <small>{copy.coverage}</small>
                <strong>
                  {coverage !== undefined ? formatPercent(coverage, language) : "—"}
                  {supplied !== undefined ? ` · ${supplied}/${expected}` : ""}
                </strong>
              </span>
            </div>
          </div>
          {prediction.warnings && prediction.warnings.length > 0 && (
            <div className="prediction-warnings">
              {prediction.warnings.map((warning) => (
                <p key={warning}>
                  <AlertTriangle aria-hidden="true" /> {warning}
                </p>
              ))}
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}

function HorizonDuel({
  data,
  language,
  copy,
}: {
  data: ObservatoryData;
  language: Language;
  copy: Copy;
}) {
  const summary =
    data.comparison.summary ??
    data.overview.horizon_comparison ??
    data.overview.comparison ??
    {};
  const ciLow = summary.ci95_lower;
  const ciHigh = summary.ci95_upper;
  const cases = data.comparison.cases ?? [];
  const conclusion =
    summary.conclusion === "inconclusive" ? copy.inconclusive : summary.conclusion ?? "—";

  return (
    <div className="duel-layout">
      <div className="duel-visual">
        <div className="duel-horizons">
          <div>
            <span className="horizon-orb may" />
            <small>{copy.mayError}</small>
            <strong>
              {formatNumber(data.evaluations.may31.metrics?.mae_days, language)} {copy.days}
            </strong>
          </div>
          <span className="versus">VS</span>
          <div>
            <span className="horizon-orb june" />
            <small>{copy.juneError}</small>
            <strong>
              {formatNumber(data.evaluations.june15.metrics?.mae_days, language)} {copy.days}
            </strong>
          </div>
        </div>
        <ComparisonPlot cases={cases} language={language} />
        <div className="plot-key">
          <span className="june-better">
            {language === "fr" ? "Juin plus précis" : "June more accurate"}
          </span>
          <span className="may-better">
            {language === "fr" ? "Mai plus précis" : "May more accurate"}
          </span>
        </div>
      </div>
      <div className="duel-verdict">
        <span className="verdict-badge">
          <FlaskConical aria-hidden="true" /> {conclusion}
        </span>
        <div className="verdict-number">
          <small>{copy.meanGain}</small>
          <strong>
            {formatNumber(
              summary.mean_delta_absolute_error_days_june_minus_may ??
                summary.mean_delta_absolute_error_days,
              language,
              3,
            )}{" "}
            <em>{copy.days}</em>
          </strong>
        </div>
        <div className="verdict-grid">
          <div>
            <small>{copy.confidenceInterval}</small>
            <strong>
              [{formatNumber(ciLow, language, 3)} ; {formatNumber(ciHigh, language, 3)}]
            </strong>
          </div>
          <div>
            <small>{copy.probability}</small>
            <strong>
              {formatPercent(summary.probability_june15_lower_error, language, 1)}
            </strong>
          </div>
          <div>
            <small>{copy.cases}</small>
            <strong>{summary.n_cases ?? data.comparison.sample_size ?? cases.length}</strong>
          </div>
        </div>
        <p>
          <ShieldCheck aria-hidden="true" />
          {language === "fr"
            ? "Le verdict suit l’intervalle statistique retourné par l’API. Aucun avantage opérationnel n’est revendiqué lorsque l’incertitude recouvre l’absence de gain."
            : "The verdict follows the statistical interval returned by the API. No operational advantage is claimed when uncertainty includes no improvement."}
        </p>
      </div>
    </div>
  );
}

interface EvidenceChamberProps {
  data: ObservatoryData;
  horizon: Horizon;
  setHorizon: (horizon: Horizon) => void;
  language: Language;
  copy: Copy;
}

function EvidenceChamber({
  data,
  horizon,
  setHorizon,
  language,
  copy,
}: EvidenceChamberProps) {
  const evaluation = data.evaluations[horizon];
  const robustness = evaluation.robustness ?? evaluation.robustness_study ?? [];
  const baseline = robustness.find((scenario) => scenario.scenario === "baseline");
  const blackouts = robustness.filter((scenario) => scenario.scenario.startsWith("missing_"));
  const maxDelta = Math.max(
    0.001,
    ...blackouts.map((scenario) =>
      Math.abs(
        scenario.delta_mae_days ??
          ((scenario.mae_days ?? 0) - (baseline?.mae_days ?? 0)),
      ),
    ),
  );
  const importance =
    evaluation.feature_importance ?? evaluation.global_feature_importance ?? [];
  const protocol = protocolFrom(data);

  return (
    <div className="evidence-grid">
      <article className="evidence-card truth-card">
        <header>
          <span className="card-icon">
            <ScanSearch aria-hidden="true" />
          </span>
          <div>
            <small>{copy.truthLens}</small>
            <h3>{copy.truthLensBody}</h3>
          </div>
          <div className="mini-switch">
            {(["may31", "june15"] as Horizon[]).map((item) => (
              <button
                type="button"
                className={item === horizon ? "active" : ""}
                key={item}
                onClick={() => setHorizon(item)}
                aria-pressed={item === horizon}
              >
                {horizonLabel(item, language)}
              </button>
            ))}
          </div>
        </header>
        <TruthLens cases={evaluation.test_cases ?? []} language={language} />
        <div className="metric-strip">
          <div>
            <small>MAE</small>
            <strong>
              {formatNumber(evaluation.metrics?.mae_days, language)} {copy.days}
            </strong>
          </div>
          <div>
            <small>RMSE</small>
            <strong>
              {formatNumber(evaluation.metrics?.rmse_days, language)} {copy.days}
            </strong>
          </div>
          <div>
            <small>{language === "fr" ? "Couverture empirique" : "Empirical coverage"}</small>
            <strong>
              {formatPercent(
                evaluation.conformal_interval?.empirical_test_coverage,
                language,
                1,
              )}
            </strong>
          </div>
          <div>
            <small>{language === "fr" ? "Cas test" : "Test cases"}</small>
            <strong>{evaluation.test_cases?.length ?? "—"}</strong>
          </div>
        </div>
      </article>

      <article className="evidence-card blackout-card">
        <header>
          <span className="card-icon amber">
            <Activity aria-hidden="true" />
          </span>
          <div>
            <small>{copy.blackout}</small>
            <h3>{copy.blackoutBody}</h3>
          </div>
        </header>
        <div className="blackout-chart">
          {blackouts.map((scenario) => {
            const delta =
              scenario.delta_mae_days ??
              ((scenario.mae_days ?? 0) - (baseline?.mae_days ?? 0));
            const modality = normalizeModality(scenario.scenario.replace("missing_", ""));
            return (
              <div className="blackout-row" key={scenario.scenario}>
                <span>{humanizeScenario(scenario.scenario, language)}</span>
                <div className="blackout-track">
                  <motion.i
                    initial={{ width: 0 }}
                    whileInView={{ width: `${(Math.abs(delta) / maxDelta) * 100}%` }}
                    viewport={{ once: true }}
                    style={{ "--bar-color": MODALITY_COLORS[modality] } as React.CSSProperties}
                  />
                </div>
                <strong className={delta < 0 ? "negative" : ""}>
                  {delta > 0 ? "+" : ""}
                  {formatNumber(delta, language, 2)}
                </strong>
              </div>
            );
          })}
        </div>
        <p className="scientific-note">
          <BarChart3 aria-hidden="true" />
          {language === "fr"
            ? "Variation de MAE en jours par rapport au scénario de référence."
            : "MAE change in days relative to the baseline scenario."}
        </p>
      </article>

      <article className="evidence-card constellation-card">
        <header>
          <span className="card-icon violet">
            <Orbit aria-hidden="true" />
          </span>
          <div>
            <small>{copy.constellation}</small>
            <h3>{copy.constellationBody}</h3>
          </div>
        </header>
        <Constellation features={importance} language={language} />
        <ol className="importance-list">
          {[...importance]
            .sort((a, b) => b.importance_mean - a.importance_mean)
            .slice(0, 5)
            .map((item) => {
              const modality = normalizeModality(item.modality, item.feature);
              return (
                <li key={item.feature}>
                  <span style={{ backgroundColor: MODALITY_COLORS[modality] }} />
                  <em>{item.feature.replaceAll("_", " ")}</em>
                  <strong>
                    {formatNumber(item.importance_mean, language, 3)}
                    {item.importance_std !== undefined && (
                      <small> ± {formatNumber(item.importance_std, language, 3)}</small>
                    )}
                  </strong>
                </li>
              );
            })}
        </ol>
        <p className="scientific-note">
          <AlertTriangle aria-hidden="true" /> {copy.globalImportance}
        </p>
      </article>

      <article className="evidence-card lineage-card">
        <header>
          <span className="card-icon green">
            <Fingerprint aria-hidden="true" />
          </span>
          <div>
            <small>{copy.lineage}</small>
            <h3>{copy.lineageBody}</h3>
          </div>
        </header>
        <div className="lineage-flow">
          <div className="lineage-node">
            <small>{copy.development}</small>
            <strong>{formatYears(protocol.development_years)}</strong>
            <span>{protocol.model_selection ?? "—"}</span>
          </div>
          <ArrowRight aria-hidden="true" />
          <div className="lineage-node">
            <small>{copy.calibration}</small>
            <strong>{protocol.calibration_year ?? "—"}</strong>
            <span>{protocol.uncertainty ?? "—"}</span>
          </div>
          <ArrowRight aria-hidden="true" />
          <div className="lineage-node protected">
            <ShieldCheck aria-hidden="true" />
            <small>{copy.untouchedTest}</small>
            <strong>{protocol.test_year ?? "—"}</strong>
            <span>{protocol.test_usage ?? "—"}</span>
          </div>
        </div>
        <div className="firewall">
          <ShieldCheck aria-hidden="true" />
          <div>
            <strong>{copy.antiLeak}</strong>
            <p>
              {language === "fr"
                ? "Disponibilité temporelle vérifiée au cutoff · variables à risque exclues."
                : "Temporal availability checked at cutoff · risky features excluded."}
            </p>
          </div>
        </div>
      </article>
    </div>
  );
}

function humanizeScenario(value: string, language: Language) {
  const names: Record<string, [string, string]> = {
    missing_soil: ["Sol absent", "Missing soil"],
    missing_sentinel1: ["Radar absent", "Missing radar"],
    missing_sentinel2: ["Optique absente", "Missing optical"],
    missing_weather: ["Météo absente", "Missing weather"],
  };
  return names[value]?.[language === "fr" ? 0 : 1] ?? value.replaceAll("_", " ");
}

function formatYears(years?: number[]) {
  if (!years?.length) return "—";
  if (years.length === 1) return String(years[0]);
  return `${Math.min(...years)}—${Math.max(...years)}`;
}

function TrustGate({
  data,
  language,
  copy,
}: {
  data: ObservatoryData;
  language: Language;
  copy: Copy;
}) {
  const evaluation = data.evaluations.june15;
  const ood = evaluation.ood ?? evaluation.ood_diagnostics;
  const target = resolveTargetNature(data);
  const limitations = Array.from(
    new Set([
      ...(data.overview.limitations ?? []),
      ...(data.evaluations.may31.limitations ?? []),
      ...(data.evaluations.june15.limitations ?? []),
    ]),
  );

  return (
    <div className="trust-shell">
      <div className="trust-orb" aria-hidden="true">
        <div>
          <ShieldCheck />
        </div>
      </div>
      <div className="trust-content">
        <p className="trust-statement">{copy.oversight}</p>
        <div className="trust-facts">
          <div>
            <Globe2 aria-hidden="true" />
            <span>
              <small>{copy.domain}</small>
              <strong>{data.overview.domain ?? "—"}</strong>
            </span>
          </div>
          <div>
            <CircleGauge aria-hidden="true" />
            <span>
              <small>{copy.ood}</small>
              <strong>{formatPercent(ood?.test_flagged_rate, language, 1)}</strong>
            </span>
          </div>
          <div>
            <Fingerprint aria-hidden="true" />
            <span>
              <small>{copy.targetNature}</small>
              <strong>{target ?? "—"}</strong>
            </span>
          </div>
          <div>
            <FlaskConical aria-hidden="true" />
            <span>
              <small>{copy.scientificStatus}</small>
              <strong>{data.overview.scientific_status ?? "—"}</strong>
            </span>
          </div>
        </div>
        {limitations.length > 0 && (
          <ul className="limitations">
            {limitations.map((limitation) => (
              <li key={limitation}>
                <AlertTriangle aria-hidden="true" /> {limitation}
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="human-loop">
        <Leaf aria-hidden="true" />
        <div>
          <small>{language === "fr" ? "Boucle humaine" : "Human in the loop"}</small>
          <strong>
            {language === "fr"
              ? "Observer · interpréter · décider"
              : "Observe · interpret · decide"}
          </strong>
        </div>
        <ArrowRight aria-hidden="true" />
      </div>
    </div>
  );
}

export default App;
