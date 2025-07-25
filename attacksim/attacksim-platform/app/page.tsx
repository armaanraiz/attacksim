import { Shield, Mail, Lock, LinkIcon, Target, TrendingUp, Award } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import Link from "next/link"

export default function HomePage() {
  // Mock user data - in real app this would come from authentication
  const isLoggedIn = false
  const userStats = {
    totalSimulations: 24,
    threatsDetected: 18,
    detectionRate: 75,
    trainingStatus: "Active",
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-blue-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Shield className="h-8 w-8" />
              <div>
                <h1 className="text-xl font-bold">AttackSim</h1>
                <p className="text-xs text-blue-100">Simulated threats. Real awareness.</p>
              </div>
            </div>

            <div className="hidden md:flex items-center space-x-8">
              <Link href="/" className="hover:text-blue-200 transition-colors">
                Home
              </Link>
              <Link href="/dashboard" className="hover:text-blue-200 transition-colors">
                Dashboard
              </Link>
              <Link href="/about" className="hover:text-blue-200 transition-colors">
                About
              </Link>
              <Link href="/help" className="hover:text-blue-200 transition-colors">
                Help
              </Link>
            </div>

            <div className="flex items-center space-x-4">
              <Button variant="ghost" className="text-white hover:bg-blue-700">
                Sign In
              </Button>
              <Button variant="secondary" className="bg-white text-blue-600 hover:bg-gray-100">
                Sign Up
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-600 via-blue-700 to-blue-800 text-white py-20">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="mb-8">
            <Shield className="h-24 w-24 mx-auto mb-6 text-blue-200" />
            <h1 className="text-5xl font-bold mb-4">AttackSim</h1>
            <p className="text-xl text-blue-100 mb-2">Simulated threats. Real awareness.</p>
            <p className="text-lg text-blue-200 max-w-3xl mx-auto">
              Master cybersecurity through realistic simulations. Learn to identify phishing emails, suspicious links,
              and fake login pages in a safe, controlled environment.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3">
              Get Started
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-3 bg-transparent"
            >
              Learn More
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Training Simulations</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Practice identifying real-world cybersecurity threats through interactive simulations
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="hover:shadow-lg transition-shadow duration-300 border-0 shadow-md">
              <CardHeader className="text-center">
                <Mail className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <CardTitle className="text-xl">Phishing Simulations</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-center text-gray-600">
                  Learn to identify suspicious emails, fake senders, and malicious attachments through realistic
                  phishing scenarios.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow duration-300 border-0 shadow-md">
              <CardHeader className="text-center">
                <Lock className="h-12 w-12 text-green-600 mx-auto mb-4" />
                <CardTitle className="text-xl">Fake Login Pages</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-center text-gray-600">
                  Practice spotting fraudulent login pages that mimic popular services like Facebook, Gmail, and banking
                  sites.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow duration-300 border-0 shadow-md">
              <CardHeader className="text-center">
                <LinkIcon className="h-12 w-12 text-orange-600 mx-auto mb-4" />
                <CardTitle className="text-xl">Suspicious Links</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-center text-gray-600">
                  Develop skills to analyze URLs, identify shortened links, and recognize potentially dangerous web
                  destinations.
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Statistics Section (shown if user is logged in) */}
      {isLoggedIn && (
        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Your Progress</h2>
              <p className="text-lg text-gray-600">Track your cybersecurity awareness improvement</p>
            </div>

            <div className="grid md:grid-cols-4 gap-6">
              <Card className="text-center border-0 shadow-md">
                <CardHeader className="pb-2">
                  <Target className="h-8 w-8 text-blue-600 mx-auto" />
                  <CardTitle className="text-2xl font-bold text-blue-600">{userStats.totalSimulations}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 font-medium">Total Simulations</p>
                </CardContent>
              </Card>

              <Card className="text-center border-0 shadow-md">
                <CardHeader className="pb-2">
                  <Shield className="h-8 w-8 text-green-600 mx-auto" />
                  <CardTitle className="text-2xl font-bold text-green-600">{userStats.threatsDetected}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 font-medium">Threats Detected</p>
                </CardContent>
              </Card>

              <Card className="text-center border-0 shadow-md">
                <CardHeader className="pb-2">
                  <TrendingUp className="h-8 w-8 text-orange-600 mx-auto" />
                  <CardTitle className="text-2xl font-bold text-orange-600">{userStats.detectionRate}%</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 font-medium">Detection Rate</p>
                  <Progress value={userStats.detectionRate} className="mt-2" />
                </CardContent>
              </Card>

              <Card className="text-center border-0 shadow-md">
                <CardHeader className="pb-2">
                  <Award className="h-8 w-8 text-cyan-600 mx-auto" />
                  <Badge variant="secondary" className="bg-cyan-100 text-cyan-800">
                    {userStats.trainingStatus}
                  </Badge>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 font-medium">Training Status</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      )}

      {/* Safety Notice */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <Alert className="border-blue-200 bg-blue-50">
            <Shield className="h-5 w-5 text-blue-600" />
            <AlertDescription className="text-blue-800">
              <strong className="font-semibold">Ethical Guidelines:</strong> AttackSim is designed for educational
              purposes only. All simulations are conducted in a controlled environment to improve cybersecurity
              awareness. Never use these techniques for malicious purposes. Always respect privacy and follow applicable
              laws and regulations.
            </AlertDescription>
          </Alert>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Shield className="h-6 w-6" />
                <span className="font-bold text-lg">AttackSim</span>
              </div>
              <p className="text-gray-400 text-sm">Simulated threats. Real awareness.</p>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Platform</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>
                  <Link href="/dashboard" className="hover:text-white transition-colors">
                    Dashboard
                  </Link>
                </li>
                <li>
                  <Link href="/simulations" className="hover:text-white transition-colors">
                    Simulations
                  </Link>
                </li>
                <li>
                  <Link href="/progress" className="hover:text-white transition-colors">
                    Progress
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>
                  <Link href="/help" className="hover:text-white transition-colors">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link href="/about" className="hover:text-white transition-colors">
                    About
                  </Link>
                </li>
                <li>
                  <Link href="/contact" className="hover:text-white transition-colors">
                    Contact
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>
                  <Link href="/privacy" className="hover:text-white transition-colors">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link href="/terms" className="hover:text-white transition-colors">
                    Terms of Service
                  </Link>
                </li>
                <li>
                  <Link href="/ethics" className="hover:text-white transition-colors">
                    Ethical Guidelines
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
            <p>&copy; 2024 AttackSim. All rights reserved. This platform is for educational purposes only.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
