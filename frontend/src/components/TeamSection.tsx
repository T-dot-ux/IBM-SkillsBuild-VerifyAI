"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { GitBranch, ExternalLink } from "lucide-react";

type GithubUser = {
  login: string;
  avatar_url: string;
  html_url: string;
  name: string;
  bio: string;
};

const teamMembers = [
  { username: "T-dot-ux", role: "Team Leader" },
  { username: "devansh3912", role: "Team Member" },
  { username: "Dhruv7946", role: "Team Member" },
  { username: "Kunal9213", role: "Team Member" },
  { username: "SaKsHaMkAkAr15", role: "Team Member" },
  { username: "yougantersingh1168-glitch", role: "Team Member" },
];

export function TeamSection() {
  const [profiles, setProfiles] = useState<Record<string, GithubUser>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfiles = async () => {
      try {
        const fetchPromises = teamMembers.map((member) =>
          fetch(`https://api.github.com/users/${member.username}`).then((res) => res.json())
        );
        const results = await Promise.all(fetchPromises);
        
        const profileMap: Record<string, GithubUser> = {};
        results.forEach((user, index) => {
          if (user.login) {
            profileMap[teamMembers[index].username] = user;
          }
        });
        setProfiles(profileMap);
      } catch (error) {
        console.error("Failed to fetch GitHub profiles", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfiles();
  }, []);

  return (
    <section className="py-20 w-full max-w-6xl mx-auto px-6 relative z-10">
      <div className="bg-white border-8 border-black p-8 md:p-12 shadow-[16px_16px_0px_0px_rgba(0,0,0,1)] rounded-3xl mb-16 relative">
        <div className="absolute -top-6 -left-6 bg-blue-500 text-white font-black px-6 py-2 border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rotate-[-5deg]">
          PROJECT DETAILS
        </div>
        <h2 className="text-4xl md:text-5xl font-black uppercase mb-6 mt-4 text-black">VerifyAI – Your Digital Trust Copilot</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-lg font-bold text-gray-800">
          <div><span className="text-blue-600">Internship:</span> AICTE | IBM SkillsBuild AI Automation & Intelligent Solutions Internship | BharatCares 2026</div>
          <div><span className="text-red-500">Team Name:</span> MATRIX PLEX</div>
          <div><span className="text-green-600">Team ID:</span> IBMBH06603</div>
          <div><span className="text-purple-600">Institution:</span> Vivekananda Institute of Professional Studies – Technical Campus, Delhi</div>
          <div><span className="text-pink-600">Team Size:</span> 6 Members</div>
        </div>
      </div>

      <div className="text-center mb-12">
        <h2 className="text-5xl md:text-6xl font-black uppercase drop-shadow-[4px_4px_0px_rgba(255,255,255,1)] text-black mb-4">Meet the Team</h2>
        <p className="text-2xl font-bold text-black bg-white inline-block px-4 py-1 border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          The minds behind MATRIX PLEX
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {teamMembers.map((member, index) => {
          const profile = profiles[member.username];
          const isLoading = loading || !profile;

          return (
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1, type: "spring", bounce: 0.4 }}
              key={member.username}
              className="bg-white border-8 border-black rounded-3xl p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-[16px_16px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-2 transition-all group relative overflow-hidden"
            >
              {isLoading ? (
                <div className="animate-pulse flex flex-col items-center">
                  <div className="w-32 h-32 bg-gray-300 rounded-full border-4 border-black mb-4"></div>
                  <div className="h-6 bg-gray-300 w-3/4 mb-2 rounded"></div>
                  <div className="h-4 bg-gray-300 w-1/2 rounded"></div>
                </div>
              ) : (
                <div className="flex flex-col items-center text-center relative z-10">
                  <div className="relative mb-6">
                    <img
                      src={profile.avatar_url}
                      alt={profile.name || member.username}
                      className="w-32 h-32 rounded-full border-8 border-black object-cover group-hover:scale-110 transition-transform duration-300"
                    />
                    <div className="absolute -bottom-4 -right-4 bg-yellow-400 p-2 rounded-full border-4 border-black group-hover:rotate-12 transition-transform">
                      <GitBranch className="w-6 h-6 text-black" />
                    </div>
                  </div>
                  
                  <h3 className="text-2xl font-black text-black uppercase mb-1">{profile.name || member.username}</h3>
                  <a
                    href={profile.html_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 font-bold hover:underline mb-2 flex items-center gap-1"
                  >
                    @{member.username} <ExternalLink className="w-3 h-3" />
                  </a>
                  
                  <div className={`mt-2 px-4 py-1 font-black uppercase text-sm border-4 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] ${
                    member.role === "Team Leader" ? "bg-red-500 text-white" : "bg-green-400 text-black"
                  }`}>
                    {member.role}
                  </div>
                  
                  {profile.bio && (
                    <p className="mt-4 text-gray-700 font-medium line-clamp-2 italic">
                      "{profile.bio}"
                    </p>
                  )}
                </div>
              )}
              
              {/* Decorative background element */}
              <div className="absolute -bottom-20 -right-20 w-40 h-40 bg-gray-100 rounded-full opacity-50 group-hover:scale-150 transition-transform duration-500 z-0"></div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
