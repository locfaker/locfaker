<div align="center">
  <img src="https://imgur.com/zeuHIk9.gif" width="489" height="407" />
</div>

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:667eea,50:764ba2,100:f093fb&height=250&section=header&fontSize=55&fontColor=ffffff&fontAlignY=40&animation=fadeIn" />
</div>

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Inter&size=24&duration=3000&pause=1000&color=667eea&center=true&vCenter=true&width=500&height=60&lines=Building+intelligent+solutions;Passionate+about+AI+%26+ML;Code+with+purpose" alt="Typing SVG" />
</div>

<div align="center">
  <img src="https://github.com/Anmol-Baranwal/Cool-GIFs-For-GitHub/assets/74038190/80728820-e06b-4f96-9c9e-9df46f0cc0a5" width="600" height="5" />
</div>

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=28&duration=2500&pause=800&color=00D9FF&center=true&vCenter=true&multiline=true&width=700&height=80&lines=💡+Problem+Solver;🌟+Tech+Enthusiast;☕+Code+with+Passion!" alt="Typing SVG" />
</div>

<div align="center">
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%">
</div>

<div align="center">
  <img src="https://github.com/VoDaiLocz/VoDaiLocz/raw/main/assets/separator.gif" width="100%">
</div>



<div align="center">
  <img src="https://github.com/VoDaiLocz/VoDaiLocz/raw/main/assets/separator.gif" width="100%">
</div>

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/VoDaiLocz/VoDaiLocz/output/github-contribution-grid-snake-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/VoDaiLocz/VoDaiLocz/output/github-contribution-grid-snake.svg">
    <img alt="github contribution grid snake animation" src="https://raw.githubusercontent.com/VoDaiLocz/VoDaiLocz/output/github-contribution-grid-snake.svg">
  </picture>
</div>

<br/>

<div align="center">
  <img src="https://raw.githubusercontent.com/VoDaiLocz/VoDaiLocz/main/assets/music-wave.svg" width="400" alt="Music Visualizer" />
</div>

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=20&pause=1000&color=7aa2f7&center=true&vCenter=true&width=400&lines=🎧+Vibing+to+the+Code;✨+Music+is+the+Energy;🌃+Creating+the+Future" alt="Music Status" />
</div>

<div align="center">
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%">
</div>

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=30&pause=1000&color=667EEA&center=true&vCenter=true&width=500&lines=🏆+GitHub+Achievements+🏆" alt="Achievements Header" />
</div>

<div align="center">
  <img src="https://github-profile-trophy.vercel.app/?username=VoDaiLocz&theme=tokyonight&no-frame=false&no-bg=true&margin-w=4&row=1&column=6" alt="GitHub Trophies" />
</div>

<br/>

<div align="center">
  <h3>📍 Quy Nhơn, Gia Lai, Việt Nam</h3>
  <h3>🤖 Robot Alpha Asimov</h3>
</div>

<br/>

<div align="center">
  <img src="https://img.shields.io/badge/Thanks%20for%20visiting!-Come%20back%20soon!-00d9ff?style=for-the-badge" alt="Thanks" />
</div>

<br/>

<div align="center">
<!-- START_SECTION:dynamic_stats -->
**Profound** (adj)  
**Định nghĩa**: Sâu sắc, uyên thâm  
**Ví dụ**: A profound effect.
<!-- Last refresh: 2026-03-03 13:19:51.208897 -->
<!-- END_SECTION:dynamic_stats -->
</div>

## 🛡️ Spring Security Research

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=24&duration=2500&pause=800&color=6DB33F&center=true&vCenter=true&width=700&lines=🔐+Spring+Security+Deep+Dive;🛡️+Securing+Java+Applications;🔑+Authentication+%26+Authorization" alt="Spring Security" />
</div>

<br/>

### 🔑 Kiến trúc Spring Security

| Thành phần | Mô tả |
|---|---|
| `SecurityFilterChain` | Chuỗi các filter xử lý request theo thứ tự |
| `AuthenticationManager` | Điều phối quá trình xác thực người dùng |
| `AuthenticationProvider` | Thực hiện xác thực (DaoAuthenticationProvider, etc.) |
| `UserDetailsService` | Load thông tin user từ database |
| `PasswordEncoder` | Mã hóa mật khẩu (BCrypt, Argon2, etc.) |
| `SecurityContextHolder` | Lưu trữ SecurityContext của request hiện tại |
| `GrantedAuthority` | Quyền hạn (role/permission) của user |

---

### 🔐 Authentication (Xác thực)

```java
// Cấu hình HTTP Security cơ bản
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/login")
                .defaultSuccessUrl("/dashboard")
                .permitAll()
            )
            .logout(logout -> logout
                .logoutSuccessUrl("/login?logout")
                .invalidateHttpSession(true)
                .deleteCookies("JSESSIONID")
            );
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(10); // strength 10 (default, doubles with each increment)
    }
}
```

---

### 🎟️ JWT (JSON Web Token)

```java
// JWT Filter - Xác thực mỗi request bằng JWT
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }
        String token = authHeader.substring(7);
        try {
            String username = jwtService.extractUsername(token);
            if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                UserDetails user = userDetailsService.loadUserByUsername(username);
                if (jwtService.isTokenValid(token, user)) {
                    UsernamePasswordAuthenticationToken authToken =
                        new UsernamePasswordAuthenticationToken(user, null, user.getAuthorities());
                    authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                    SecurityContextHolder.getContext().setAuthentication(authToken);
                }
            }
        } catch (Exception e) {
            // Token không hợp lệ hoặc hết hạn – không set authentication
            SecurityContextHolder.clearContext();
        }
        filterChain.doFilter(request, response);
    }
}
```

> ⚠️ **Lưu ý bảo mật JWT:**
> - Luôn dùng thuật toán **RS256** hoặc **HS256** với key đủ mạnh (≥256 bit)
> - Đặt thời hạn token ngắn (15–60 phút) + dùng Refresh Token
> - **Không** lưu JWT vào `localStorage` (dễ bị XSS); ưu tiên `HttpOnly Cookie`
> - Validate đầy đủ: signature, expiry, issuer, audience

---

### 🌐 OAuth2 & OpenID Connect

```java
// Cấu hình OAuth2 Login (Google, GitHub, ...)
@Bean
public SecurityFilterChain oauth2FilterChain(HttpSecurity http) throws Exception {
    http
        .oauth2Login(oauth2 -> oauth2
            .loginPage("/oauth2/authorization/google")
            .defaultSuccessUrl("/home", true)
            .userInfoEndpoint(userInfo -> userInfo
                .userService(customOAuth2UserService)
            )
        )
        .oauth2ResourceServer(oauth2 -> oauth2
            .jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthConverter()))
        );
    return http.build();
}
```

> **PKCE (Proof Key for Code Exchange):** Bắt buộc với public clients (SPA, mobile) và được khuyến nghị cho tất cả client types (OAuth 2.1+) để ngăn Authorization Code Interception Attack.

---

### 🔒 Authorization (Phân quyền)

```java
// Method Security - Bảo vệ ở tầng Service
@Configuration
@EnableMethodSecurity // thay @EnableGlobalMethodSecurity trong Spring 6+
public class MethodSecurityConfig {}

@Service
public class ArticleService {

    @PreAuthorize("hasRole('ADMIN') or #article.authorId == authentication.principal.id")
    public void deleteArticle(Article article) { ... }

    @PostAuthorize("returnObject.authorId == authentication.principal.id")
    public Article getArticle(Long id) { ... }

    @PreAuthorize("hasAuthority('article:write')")
    public Article createArticle(Article article) { ... }
}
```

| Annotation | Mô tả |
|---|---|
| `@PreAuthorize` | Kiểm tra quyền **trước** khi thực thi method |
| `@PostAuthorize` | Kiểm tra quyền **sau** khi thực thi (dựa trên kết quả) |
| `@Secured` | Kiểm tra role đơn giản (ít linh hoạt hơn) |
| `@RolesAllowed` | Tương tự `@Secured`, chuẩn JSR-250 |

---

### 🚫 CSRF Protection

```java
// CSRF: Bật mặc định với Session-based auth; tắt khi dùng JWT (stateless)
http
    .csrf(csrf -> csrf
        // Tắt CSRF cho REST API dùng JWT
        .disable()
        // Hoặc chỉ tắt cho API endpoints
        // .ignoringRequestMatchers("/api/**")
    );

// Nếu giữ CSRF, dùng CookieCsrfTokenRepository cho SPA
http.csrf(csrf -> csrf
    .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
);
```

> ⚠️ **Không bao giờ tắt CSRF với ứng dụng dùng Session/Cookie authentication!**

---

### 🔓 Common Vulnerabilities & Fixes

| Lỗ hổng | Nguyên nhân | Giải pháp |
|---|---|---|
| **Broken Authentication** | Mật khẩu yếu, session không hết hạn | BCrypt + session timeout |
| **SQL Injection** | Query ghép chuỗi thủ công | Spring Data JPA / Prepared Statements |
| **XSS** | Render HTML không encode | Content Security Policy + output encoding |
| **CSRF** | Request giả mạo từ site khác | CSRF token / SameSite Cookie |
| **IDOR** | Không kiểm tra quyền sở hữu resource | `@PostAuthorize` / ownership check |
| **JWT none algorithm** | Không validate `alg` header | Whitelist algorithms, reject `none` |
| **Mass Assignment** | Bind trực tiếp request body vào entity | Dùng DTO, `@JsonIgnore` trên sensitive fields |
| **Open Redirect** | Redirect URL không validate | Whitelist redirect URLs |

---

### 🔧 Security Headers (Best Practices)

```java
http.headers(headers -> headers
    .frameOptions(frame -> frame.deny())                        // Chống Clickjacking
    .contentTypeOptions(Customizer.withDefaults())              // Chống MIME sniffing
    .httpStrictTransportSecurity(hsts -> hsts                   // Bắt buộc HTTPS
        .includeSubDomains(true)
        .maxAgeInSeconds(31536000)
    )
    .contentSecurityPolicy(csp -> csp
        .policyDirectives("default-src 'self'; script-src 'self'") // Chống XSS (ưu tiên hơn X-XSS-Protection đã deprecated)
    )
);
```

---

### 🏗️ Stateless vs Stateful Security

| | **Stateful (Session)** | **Stateless (JWT)** |
|---|---|---|
| Lưu trạng thái | Server-side (HttpSession) | Client-side (Token) |
| Scale | Cần sticky session / Redis | Dễ horizontal scale |
| Revoke token | Dễ (xóa session) | Khó (cần blacklist / short TTL) |
| CSRF | Cần bảo vệ | Không cần (nếu không dùng Cookie) |
| Phù hợp | Web app truyền thống (MVC) | REST API, Microservices |

---

### 📚 Tài nguyên học Spring Security

- 📖 [Spring Security Reference Docs](https://docs.spring.io/spring-security/reference/)
- 🎓 [Spring Security Architecture](https://spring.io/guides/topicals/spring-security-architecture)
- 🔐 [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- 🛡️ [JWT Best Practices (RFC 8725)](https://datatracker.ietf.org/doc/html/rfc8725)
- 📦 [Baeldung Spring Security](https://www.baeldung.com/security-spring)

<div align="center">
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%">
</div>

---

## <img src="https://media.giphy.com/media/fsEaZldNC8A1PJ3mwp/giphy.gif" width="60"> <b>Quote của ngày</b>

<br/>

<div align="center">
  <img src="https://quotes-github-readme.vercel.app/api?type=horizontal&theme=tokyonight&border=true" />
</div>

<br/>

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=24&duration=3000&pause=1000&color=00D9FF&center=true&vCenter=true&width=600&height=60&lines=Thanks+for+visiting+my+profile!+🙏;Let's+build+something+amazing+together!+🚀;Happy+coding!+💻✨" alt="Thanks Message" />
</div>

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=footer&animation=fadeIn" />
</div>
