function App() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-12">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-300">
            FareRadar
          </p>
          <h1 className="mt-4 text-4xl font-semibold tracking-normal text-white sm:text-5xl">
            Monitoreo inteligente de ofertas de vuelos
          </h1>
          <p className="mt-5 text-lg leading-8 text-slate-300">
            Bootstrap inicial listo: React, Vite, TypeScript y Tailwind preparados para el
            dashboard de watchlists, ofertas e historial de precios.
          </p>
          <div className="mt-8 grid gap-3 text-sm text-slate-300 sm:grid-cols-3">
            <div className="border border-slate-800 bg-slate-900 p-4">
              <span className="block text-cyan-300">Backend</span>
              FastAPI API-first
            </div>
            <div className="border border-slate-800 bg-slate-900 p-4">
              <span className="block text-cyan-300">Workers</span>
              Redis + Celery
            </div>
            <div className="border border-slate-800 bg-slate-900 p-4">
              <span className="block text-cyan-300">Deploy</span>
              Railway ready
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

export default App;
