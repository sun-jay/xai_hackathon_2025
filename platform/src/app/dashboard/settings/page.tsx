import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-light text-foreground">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Manage your account settings and preferences.
        </p>
      </div>

      <div className="rounded-xl border border-border bg-card p-6 space-y-6">
        <div>
          <h2 className="text-xl font-light text-foreground mb-4">Profile</h2>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground uppercase tracking-wider block mb-2">
                Name
              </label>
              <input
                type="text"
                placeholder="Your name"
                className="w-full max-w-md px-4 py-2 rounded-lg border border-border bg-input text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground uppercase tracking-wider block mb-2">
                Email
              </label>
              <input
                type="email"
                placeholder="your@email.com"
                className="w-full max-w-md px-4 py-2 rounded-lg border border-border bg-input text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
          </div>
        </div>

        <div className="border-t border-border pt-6">
          <h2 className="text-xl font-light text-foreground mb-4">
            Preferences
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between max-w-md">
              <div>
                <p className="text-foreground font-medium">
                  Email Notifications
                </p>
                <p className="text-muted-foreground text-sm">
                  Receive email updates about your interviews
                </p>
              </div>
              <div className="size-6 rounded-full bg-primary/20 border-2 border-primary" />
            </div>
          </div>
        </div>

        <div className="border-t border-border pt-6">
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
            Save Changes
          </Button>
        </div>
      </div>
    </div>
  );
}

