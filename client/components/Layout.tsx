import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Brain,
  TrendingDown,
  MessageSquare,
  GraduationCap,
  FileText,
  DollarSign,
  BookOpen,
  Calendar,
  Users,
  Menu,
  Sparkles,
  LogOut,
  User,
  Settings,
  Shield,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";

const navigationItems = [
  {
    name: "Dashboard",
    href: "/",
    icon: Brain,
  },
  {
    name: "Résumé-Job Fit Engine",
    href: "/resume-fit",
    icon: FileText,
  },
  {
    name: "Turnover & Retention",
    href: "/turnover-retention",
    icon: TrendingDown,
  },
  {
    name: "Interview Co-pilot",
    href: "/interview-copilot",
    icon: MessageSquare,
  },
  {
    name: "Onboarding Journey",
    href: "/onboarding",
    icon: GraduationCap,
  },
  {
    name: "Performance Feedback",
    href: "/performance",
    icon: FileText,
  },
  {
    name: "Compensation Analysis",
    href: "/compensation",
    icon: DollarSign,
  },
  {
    name: "Learning Paths",
    href: "/learning-paths",
    icon: BookOpen,
  },
  {
    name: "Attendance Analytics",
    href: "/attendance",
    icon: Calendar,
  },
  {
    name: "Diversity & Inclusion",
    href: "/diversity-inclusion",
    icon: Users,
  },
];

const adminNavigationItems = [
  {
    name: "Admin: Role Predictor",
    href: "/admin/role-predictor",
    icon: Shield,
  },
];

interface LayoutProps {
  children: React.ReactNode;
}

function Navigation({ isAdmin }: { isAdmin: boolean }) {
  const location = useLocation();

  const items = [...navigationItems, ...(isAdmin ? adminNavigationItems : [])];

  return (
    <nav className="space-y-2">
      {items.map((item) => {
        const Icon = item.icon;
        const isActive = location.pathname === item.href;

        return (
          <Link
            key={item.href}
            to={item.href}
            className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all hover:bg-secondary ${
              isActive
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <Icon className="h-4 w-4" />
            {item.name}
          </Link>
        );
      })}
    </nav>
  );
}

export default function Layout({ children }: LayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const isAdmin = user?.role === 'admin';

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col">
        <div className="flex flex-col h-full bg-card border-r">
          <div className="flex items-center gap-2 h-16 px-6 border-b">
            <div className="flex items-center justify-center w-8 h-8 bg-primary rounded-lg">
              <Sparkles className="h-4 w-4 text-primary-foreground" />
            </div>
            <div>
              <h1 className="font-semibold text-lg">HRGenius</h1>
              <p className="text-xs text-muted-foreground">AI-Powered HR</p>
            </div>
          </div>
          <ScrollArea className="flex-1 p-4">
            <Navigation isAdmin={isAdmin} />
          </ScrollArea>
          {isAuthenticated && (
            <div className="p-4 border-t">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="w-full justify-start gap-3 h-auto px-3 py-2">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={`https://ui-avatars.com/api/?name=${encodeURIComponent(user?.username || 'User')}&background=random`} />
                      <AvatarFallback>{user?.username?.[0].toUpperCase() || 'U'}</AvatarFallback>
                    </Avatar>
                    <div className="text-left flex-1">
                      <p className="text-sm font-medium truncate">{user?.username}</p>
                      <p className="text-xs text-muted-foreground truncate capitalize">{user?.role}</p>
                    </div>
                    <Settings className="h-4 w-4 text-muted-foreground" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{user?.username}</p>
                      <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => navigate("/resume-fit")}>
                    <User className="mr-2 h-4 w-4" />
                    My Resumes
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate("/resume-ranking")}>
                    <FileText className="mr-2 h-4 w-4" />
                    Resume Ranking
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="text-destructive focus:text-destructive">
                    <LogOut className="mr-2 h-4 w-4" />
                    Log out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Header */}
      <div className="md:hidden">
        <div className="flex items-center justify-between h-16 px-4 border-b bg-background">
          <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64 p-0">
              <div className="flex items-center gap-2 h-16 px-6 border-b">
                <div className="flex items-center justify-center w-8 h-8 bg-primary rounded-lg">
                  <Sparkles className="h-4 w-4 text-primary-foreground" />
                </div>
                <div>
                  <h1 className="font-semibold text-lg">HRGenius</h1>
                  <p className="text-xs text-muted-foreground">AI-Powered HR</p>
                </div>
              </div>
              <ScrollArea className="flex-1 p-4">
                <Navigation isAdmin={isAdmin} />
              </ScrollArea>
            </SheetContent>
          </Sheet>
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center w-8 h-8 bg-primary rounded-lg">
              <Sparkles className="h-4 w-4 text-primary-foreground" />
            </div>
            <div>
              <h1 className="font-semibold text-lg">HRGenius</h1>
              <p className="text-xs text-muted-foreground">AI-Powered HR</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}