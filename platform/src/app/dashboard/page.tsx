export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-light text-foreground">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Welcome to your Grok Recruiter dashboard.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-xl border border-border bg-card p-6">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-2">
            Total Interviews
          </h3>
          <p className="text-3xl font-light text-foreground">24</p>
        </div>
        <div className="rounded-xl border border-border bg-card p-6">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-2">
            Completed
          </h3>
          <p className="text-3xl font-light text-foreground">18</p>
        </div>
        <div className="rounded-xl border border-border bg-card p-6">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-2">
            Pending
          </h3>
          <p className="text-3xl font-light text-foreground">6</p>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card p-6">
        <h2 className="text-xl font-light text-foreground mb-4">
          Recent Activity
        </h2>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="flex items-center gap-4 p-4 rounded-lg bg-muted/50"
            >
              <div className="size-10 rounded-full bg-primary/20 flex items-center justify-center">
                <span className="text-primary text-sm font-medium">{i}</span>
              </div>
              <div className="flex-1">
                <p className="text-foreground font-medium">Interview {i}</p>
                <p className="text-muted-foreground text-sm">
                  Completed on Dec {i + 4}, 2025
                </p>
              </div>
              <span className="text-xs font-mono uppercase px-2 py-1 rounded bg-primary/10 text-primary">
                Complete
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
