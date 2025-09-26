import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Back from ".././assets/BackGround.png";
import { GoogleSignInButton } from "@/components/GoogleSignInButton";

export default function SignupPage() {
    return (
        <div className="flex min-h-screen">
            {/* Left Image */}

            <div className="hidden md:flex w-1/2 bg-cover bg-center">
                <img
                    className="w-full h-full rotate-[-180] object-cover"
                    src={Back}
                    alt="Just a image here"
                ></img>
            </div>

            {/* Right Sign Up Form */}
            <div className="flex flex-col justify-center items-center w-full md:w-1/2 bg-gray-900 text-white p-8">
                <div className="w-full max-w-md">
                    <h1 className="text-2xl font-bold mb-2 text-center">
                        Create an Account
                    </h1>
                    <p className="text-gray-400 mb-6 text-center">
                        Fill in your details to get started
                    </p>

                    <form className="flex flex-col gap-4">
                        {/* Name */}
                        <div>
                            <Label htmlFor="name" className="text-gray-300">
                                Name
                            </Label>
                            <Input
                                id="name"
                                type="text"
                                placeholder="John Doe"
                                className="bg-gray-800 text-white border-gray-700"
                            />
                        </div>

                        {/* Email */}
                        <div>
                            <Label htmlFor="email" className="text-gray-300">
                                Email
                            </Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="name@example.com"
                                className="bg-gray-800 text-white border-gray-700"
                            />
                        </div>

                        {/* Password */}
                        <div>
                            <Label htmlFor="password" className="text-gray-300">
                                Password
                            </Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="********"
                                className="bg-gray-800 text-white border-gray-700"
                            />
                        </div>

                        <Button
                            type="submit"
                            className="w-full bg-white text-gray-900 hover:bg-gray-100 mt-2"
                        >
                            Sign Up with Email
                        </Button>
                    </form>

                    <div className="flex items-center my-4">
                        <hr className="flex-grow border-gray-700" />
                        <span className="px-2 text-gray-500 text-sm">
                            OR CONTINUE WITH
                        </span>
                        <hr className="flex-grow border-gray-700" />
                    </div>

                    <GoogleSignInButton />

                    <p className="text-gray-500 text-xs mt-6 text-center">
                        By clicking continue, you agree to our{" "}
                        <a href="/terms" className="underline text-gray-400">
                            Terms of Service
                        </a>{" "}
                        and{" "}
                        <a href="/privacy" className="underline text-gray-400">
                            Privacy Policy
                        </a>
                        .
                    </p>
                </div>
            </div>
        </div>
    );
}
