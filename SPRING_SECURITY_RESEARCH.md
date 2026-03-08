# Spring Security – Nghiên Cứu Toàn Diện

> **Mục tiêu**: Nghiên cứu thật kĩ mọi vấn đề liên quan đến Spring Security – từ kiến trúc nội tại đến cấu hình thực tế, các cơ chế xác thực/phân quyền, bảo vệ chống tấn công, và best practices trong môi trường production.

---

## Mục Lục

1. [Tổng quan & Kiến trúc](#1-tổng-quan--kiến-trúc)
2. [Security Filter Chain](#2-security-filter-chain)
3. [Authentication – Xác thực](#3-authentication--xác-thực)
4. [Authorization – Phân quyền](#4-authorization--phân-quyền)
5. [SecurityContext & SecurityContextHolder](#5-securitycontext--securitycontextholder)
6. [Password Encoding](#6-password-encoding)
7. [Session Management](#7-session-management)
8. [CSRF Protection](#8-csrf-protection)
9. [CORS](#9-cors)
10. [OAuth2 & OpenID Connect](#10-oauth2--openid-connect)
11. [JWT (JSON Web Token)](#11-jwt-json-web-token)
12. [HTTP Basic & Digest Authentication](#12-http-basic--digest-authentication)
13. [LDAP Authentication](#13-ldap-authentication)
14. [Remember-Me Authentication](#14-remember-me-authentication)
15. [Method-Level Security](#15-method-level-security)
16. [ACL (Access Control List)](#16-acl-access-control-list)
17. [Security Events & Audit Logging](#17-security-events--audit-logging)
18. [Các Lỗ Hổng Phổ Biến & Biện Pháp](#18-các-lỗ-hổng-phổ-biến--biện-pháp)
19. [Spring Boot Auto-Configuration](#19-spring-boot-auto-configuration)
20. [Testing Spring Security](#20-testing-spring-security)
21. [Best Practices & Checklist Production](#21-best-practices--checklist-production)

---

## 1. Tổng quan & Kiến trúc

### 1.1 Spring Security là gì?

Spring Security là framework bảo mật mạnh mẽ, linh hoạt dành cho các ứng dụng Java. Nó cung cấp:

- **Authentication**: Xác định _ai_ đang truy cập hệ thống.
- **Authorization**: Xác định _được phép làm gì_.
- **Protection against attacks**: CSRF, Session fixation, Clickjacking, XSS headers, ...

### 1.2 Các khái niệm cốt lõi

| Khái niệm | Mô tả |
|---|---|
| `Principal` | Thực thể đang thực hiện hành động (user, service, device) |
| `Authentication` | Quá trình xác minh danh tính của principal |
| `Authorization` | Quá trình kiểm tra quyền hạn của principal đã xác thực |
| `GrantedAuthority` | Quyền hạn được cấp cho principal (role, permission) |
| `SecurityContext` | Nơi lưu trữ thông tin xác thực trong phạm vi một request |
| `UserDetails` | Interface mô tả thông tin user trong hệ thống |

### 1.3 Kiến trúc tổng thể

```
HTTP Request
     │
     ▼
┌─────────────────────────────────────┐
│         DelegatingFilterProxy       │  ← Servlet Container filter
│   (bridges Servlet ↔ Spring Bean)   │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│       FilterChainProxy              │  ← Spring Bean, manages chains
│  ┌───────────────────────────────┐  │
│  │  SecurityFilterChain #1       │  │  ← for /api/**
│  │  SecurityFilterChain #2       │  │  ← for /admin/**
│  │  SecurityFilterChain #n       │  │  ← default
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
     │
     ▼ (matched chain)
[Filter 1] → [Filter 2] → ... → [Filter N] → DispatcherServlet
```

---

## 2. Security Filter Chain

### 2.1 Danh sách các filter mặc định (theo thứ tự)

| Thứ tự | Filter | Nhiệm vụ |
|---|---|---|
| 100 | `DisableEncodeUrlFilter` | Ngăn URL chứa sessionId |
| 200 | `WebAsyncManagerIntegrationFilter` | Tích hợp SecurityContext với async |
| 300 | `SecurityContextHolderFilter` | Load/Save SecurityContext |
| 400 | `HeaderWriterFilter` | Thêm security headers vào response |
| 500 | `CorsFilter` | Xử lý CORS |
| 600 | `CsrfFilter` | Kiểm tra CSRF token |
| 700 | `LogoutFilter` | Xử lý logout request |
| 800 | `UsernamePasswordAuthenticationFilter` | Form login |
| 900 | `DefaultLoginPageGeneratingFilter` | Tạo trang login mặc định |
| 1000 | `DefaultLogoutPageGeneratingFilter` | Tạo trang logout mặc định |
| 1100 | `BasicAuthenticationFilter` | HTTP Basic auth |
| 1200 | `RequestCacheAwareFilter` | Redirect về URL gốc sau login |
| 1300 | `SecurityContextHolderAwareRequestWrapper` | Bọc request với security API |
| 1400 | `AnonymousAuthenticationFilter` | Tạo anonymous user nếu chưa login |
| 1500 | `SessionManagementFilter` | Xử lý session fixation, concurrent sessions |
| 1600 | `ExceptionTranslationFilter` | Bắt AuthException và AccessDeniedException |
| 1700 | `AuthorizationFilter` | Kiểm tra authorization |

### 2.2 Cấu hình SecurityFilterChain (Spring Boot 3.x / Spring Security 6.x)

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**", "/actuator/health").permitAll()
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/login")
                .defaultSuccessUrl("/dashboard", true)
                .permitAll()
            )
            .logout(logout -> logout
                .logoutUrl("/logout")
                .logoutSuccessUrl("/login?logout")
                .invalidateHttpSession(true)
                .deleteCookies("JSESSIONID")
            )
            .csrf(csrf -> csrf.ignoringRequestMatchers("/api/**"))
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
                .maximumSessions(1)
                .maxSessionsPreventsLogin(false)
            );

        return http.build();
    }
}
```

### 2.3 Thêm custom filter

```java
// Filter tự định nghĩa
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain)
            throws ServletException, IOException {

        String token = extractToken(request);
        if (token != null && jwtService.isValid(token)) {
            Authentication auth = jwtService.getAuthentication(token);
            SecurityContextHolder.getContext().setAuthentication(auth);
        }
        chain.doFilter(request, response);
    }
}

// Đăng ký filter vào chain
http.addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);
```

---

## 3. Authentication – Xác thực

### 3.1 Luồng xác thực tổng quát

```
Request
  │
  ▼
AuthenticationFilter
  │  extracts credentials
  ▼
Authentication (token, chưa xác thực)
  │
  ▼
AuthenticationManager (ProviderManager)
  │  delegates to matching provider
  ▼
AuthenticationProvider
  │  loads user, validates credentials
  ▼
UserDetailsService.loadUserByUsername()
  │
  ▼
Authentication (đã xác thực, với GrantedAuthority list)
  │
  ▼
SecurityContextHolder.getContext().setAuthentication(auth)
```

### 3.2 UserDetailsService

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {

    @Autowired
    private UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String username)
            throws UsernameNotFoundException {

        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException(
                "User not found: " + username));

        return org.springframework.security.core.userdetails.User
            .withUsername(user.getUsername())
            .password(user.getPassword())          // already encoded
            .roles(user.getRoles().toArray(new String[0]))
            .accountExpired(!user.isActive())      // accountExpired=true khi account không còn active
            .credentialsExpired(user.isPasswordExpired())
            .disabled(!user.isEnabled())
            .build();
    }
}
```

### 3.3 AuthenticationProvider tùy chỉnh

```java
@Component
public class CustomAuthProvider implements AuthenticationProvider {

    @Autowired
    private UserDetailsService userDetailsService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    public Authentication authenticate(Authentication authentication)
            throws AuthenticationException {

        String username = authentication.getName();
        String password = authentication.getCredentials().toString();

        UserDetails user = userDetailsService.loadUserByUsername(username);

        if (!passwordEncoder.matches(password, user.getPassword())) {
            throw new BadCredentialsException("Invalid credentials");
        }

        return new UsernamePasswordAuthenticationToken(
            user, null, user.getAuthorities());
    }

    @Override
    public boolean supports(Class<?> authType) {
        return UsernamePasswordAuthenticationToken.class.isAssignableFrom(authType);
    }
}
```

### 3.4 ProviderManager – AuthenticationManager

```java
@Bean
public AuthenticationManager authenticationManager(
        AuthenticationConfiguration config) throws Exception {
    return config.getAuthenticationManager();
}

// Hoặc tự cấu hình:
@Bean
public AuthenticationManager authenticationManager(
        UserDetailsService userDetailsService,
        PasswordEncoder encoder) {

    DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
    provider.setUserDetailsService(userDetailsService);
    provider.setPasswordEncoder(encoder);
    return new ProviderManager(provider);
}
```

---

## 4. Authorization – Phân quyền

### 4.1 URL-based Authorization

```java
http.authorizeHttpRequests(auth -> auth
    // Exact path
    .requestMatchers("/login", "/register").permitAll()
    // Wildcard
    .requestMatchers("/public/**").permitAll()
    // HTTP method + path
    .requestMatchers(HttpMethod.GET, "/api/products/**").permitAll()
    .requestMatchers(HttpMethod.POST, "/api/products/**").hasRole("ADMIN")
    // SpEL expression
    .requestMatchers("/profile").access(
        new WebExpressionAuthorizationManager("isAuthenticated() and #username == principal.username"))
    // Role hierarchy
    .requestMatchers("/manager/**").hasAnyRole("MANAGER", "ADMIN")
    .anyRequest().authenticated()
);
```

### 4.2 Role Hierarchy

```java
@Bean
public RoleHierarchy roleHierarchy() {
    RoleHierarchyImpl hierarchy = new RoleHierarchyImpl();
    hierarchy.setHierarchy("""
        ROLE_ADMIN > ROLE_MANAGER
        ROLE_MANAGER > ROLE_USER
        ROLE_USER > ROLE_GUEST
        """);
    return hierarchy;
}
```

### 4.3 Method-Level Security

Bật bằng annotation:

```java
@Configuration
@EnableMethodSecurity   // Spring Security 6+
// @EnableGlobalMethodSecurity(prePostEnabled = true)  // cũ
public class MethodSecurityConfig { }
```

Các annotation:

```java
// Kiểm tra trước khi thực thi
@PreAuthorize("hasRole('ADMIN')")
@PreAuthorize("hasAuthority('user:read')")
@PreAuthorize("#userId == authentication.principal.id or hasRole('ADMIN')")
@PreAuthorize("@permissionService.canAccess(authentication, #resourceId)")
public Resource getResource(Long userId, Long resourceId) { ... }

// Lọc kết quả trả về
@PostAuthorize("returnObject.owner == authentication.name")
public Document findDocument(Long id) { ... }

// Lọc tham số đầu vào (Collection)
@PreFilter("filterObject.owner == authentication.name")
public void processDocuments(List<Document> docs) { ... }

// Lọc kết quả Collection
@PostFilter("filterObject.visibility == 'PUBLIC' or filterObject.owner == authentication.name")
public List<Document> findAll() { ... }

// JSR-250 annotations
@RolesAllowed({"ADMIN", "MANAGER"})
@DenyAll
@PermitAll
public void adminAction() { ... }

// Spring's @Secured
@Secured("ROLE_ADMIN")
public void securedMethod() { ... }
```

---

## 5. SecurityContext & SecurityContextHolder

### 5.1 Lấy thông tin user hiện tại

```java
// Cách 1: SecurityContextHolder
Authentication auth = SecurityContextHolder.getContext().getAuthentication();
String username = auth.getName();
Collection<? extends GrantedAuthority> authorities = auth.getAuthorities();

// Cách 2: Inject Authentication vào Controller
@GetMapping("/me")
public ResponseEntity<?> getCurrentUser(Authentication authentication) {
    return ResponseEntity.ok(authentication.getPrincipal());
}

// Cách 3: @AuthenticationPrincipal
@GetMapping("/me")
public ResponseEntity<?> getCurrentUser(
        @AuthenticationPrincipal UserDetails userDetails) {
    return ResponseEntity.ok(userDetails.getUsername());
}

// Cách 4: Custom annotation
@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
@AuthenticationPrincipal(expression = "user")
public @interface CurrentUser { }
```

### 5.2 SecurityContextHolder Strategies

```java
// Thread-local (mặc định) – mỗi thread có SecurityContext riêng
SecurityContextHolder.setStrategyName(
    SecurityContextHolder.MODE_THREADLOCAL);

// InheritableThreadLocal – child thread kế thừa context từ parent
SecurityContextHolder.setStrategyName(
    SecurityContextHolder.MODE_INHERITABLETHREADLOCAL);

// Global – toàn bộ JVM dùng chung 1 context (dùng cho standalone app)
SecurityContextHolder.setStrategyName(
    SecurityContextHolder.MODE_GLOBAL);
```

### 5.3 Bảo toàn SecurityContext trong Async

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.initialize();
        // Bao bọc để propagate SecurityContext sang async thread
        return new DelegatingSecurityContextAsyncTaskExecutor(executor);
    }
}
```

---

## 6. Password Encoding

### 6.1 PasswordEncoder implementations

| Encoder | Mô tả | Khuyến nghị |
|---|---|---|
| `BCryptPasswordEncoder` | BCrypt – adaptive, cost factor 4-31 | ✅ Khuyến nghị |
| `Argon2PasswordEncoder` | Argon2id – winner PHC 2015 | ✅ Tốt nhất cho security mới |
| `SCryptPasswordEncoder` | scrypt – memory-hard | ✅ Tốt |
| `Pbkdf2PasswordEncoder` | PBKDF2 – FIPS-approved | ✅ Khi cần FIPS |
| `NoOpPasswordEncoder` | Plaintext | ❌ Chỉ cho dev/test |
| `MD5PasswordEncoder` | MD5 | ❌ Deprecated |

### 6.2 DelegatingPasswordEncoder – Khuyến nghị

```java
@Bean
public PasswordEncoder passwordEncoder() {
    // Dùng bcrypt mặc định, nhưng có thể upgrade/downgrade dễ dàng
    return PasswordEncoderFactories.createDelegatingPasswordEncoder();
}
```

Mật khẩu được lưu với prefix: `{bcrypt}$2a$10$...`, `{argon2}$argon2id$...`

```java
// Tùy chỉnh DelegatingPasswordEncoder
Map<String, PasswordEncoder> encoders = new HashMap<>();
encoders.put("bcrypt", new BCryptPasswordEncoder(12));
encoders.put("argon2", Argon2PasswordEncoder.defaultsForSpringSecurity_v5_8());

PasswordEncoder encoder = new DelegatingPasswordEncoder("bcrypt", encoders);
```

### 6.3 BCrypt cost factor

```java
// strength (cost factor) từ 4-31, mặc định 10
// Mỗi tăng 1 đơn vị = tăng gấp đôi thời gian hash
// Target: ~1 giây trên server production
BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

// Test thời gian hash
long start = System.currentTimeMillis();
encoder.encode("password");
System.out.println("BCrypt strength 12: " + (System.currentTimeMillis() - start) + "ms");
```

---

## 7. Session Management

### 7.1 Session creation policies

```java
http.sessionManagement(session -> session
    // Tạo session nếu cần (mặc định)
    .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
    // Không bao giờ tạo session, nhưng dùng nếu đã có
    .sessionCreationPolicy(SessionCreationPolicy.NEVER)
    // Không dùng session (stateless – cho REST API)
    .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
    // Luôn tạo session mới
    .sessionCreationPolicy(SessionCreationPolicy.ALWAYS)
);
```

### 7.2 Session Fixation Protection

```java
http.sessionManagement(session -> session
    // Tạo session ID mới sau khi login (mặc định – khuyến nghị)
    .sessionFixation().changeSessionId()
    // Tạo session mới và migrate attributes
    .sessionFixation().migrateSession()
    // Tạo session mới, KHÔNG migrate attributes
    .sessionFixation().newSession()
    // Không bảo vệ (không khuyến nghị)
    .sessionFixation().none()
);
```

### 7.3 Concurrent Session Control

```java
@Bean
public HttpSessionEventPublisher httpSessionEventPublisher() {
    return new HttpSessionEventPublisher();
}

http.sessionManagement(session -> session
    .maximumSessions(1)
    // true: block login mới nếu đã đủ session
    // false: đẩy session cũ ra (mặc định)
    .maxSessionsPreventsLogin(true)
    .expiredUrl("/login?expired")
);
```

### 7.4 Session Timeout & Security

```properties
# application.properties
server.servlet.session.timeout=30m
server.servlet.session.cookie.http-only=true
server.servlet.session.cookie.secure=true
server.servlet.session.cookie.same-site=Strict
```

---

## 8. CSRF Protection

### 8.1 CSRF là gì và cách Spring Security bảo vệ

Cross-Site Request Forgery (CSRF) là tấn công buộc user đã xác thực thực hiện hành động không mong muốn.

Spring Security sử dụng **Synchronizer Token Pattern**:
1. Server tạo CSRF token ngẫu nhiên, lưu trong session
2. Mọi state-changing request (POST, PUT, DELETE, PATCH) phải kèm token
3. Server so sánh token từ request với token trong session

### 8.2 Cấu hình CSRF

```java
// Bật CSRF (mặc định với web app)
http.csrf(Customizer.withDefaults());

// Tắt CSRF (cho stateless API – dùng JWT)
http.csrf(csrf -> csrf.disable());

// Tắt cho một số endpoint
http.csrf(csrf -> csrf
    .ignoringRequestMatchers("/api/webhook/**")
    .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
);
```

### 8.3 CSRF với SPA (Single Page Application)

```java
// Dùng cookie-based CSRF token cho SPA (Angular, React)
http.csrf(csrf -> csrf
    .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
    .csrfTokenRequestHandler(new XorCsrfTokenRequestAttributeHandler())
);
```

```javascript
// Phía client (Angular): HTTPClientModule tự động gửi X-XSRF-TOKEN header
// Phía client (React): lấy token từ cookie và gửi trong header
const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('XSRF-TOKEN='))
    ?.split('=')[1];

fetch('/api/data', {
    method: 'POST',
    headers: { 'X-XSRF-TOKEN': csrfToken }
});
```

### 8.4 Thymeleaf integration

```html
<!-- Tự động thêm CSRF token vào form -->
<form th:action="@{/process}" method="post">
    <input type="hidden" th:name="${_csrf.parameterName}" th:value="${_csrf.token}"/>
    ...
</form>
```

---

## 9. CORS

### 9.1 Cấu hình CORS trong Spring Security

```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://example.com", "https://app.example.com"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowedHeaders(List.of("Authorization", "Content-Type", "X-XSRF-TOKEN"));
    config.setExposedHeaders(List.of("X-Total-Count"));
    config.setAllowCredentials(true);
    config.setMaxAge(3600L);

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return source;
}

// Kích hoạt trong SecurityFilterChain
http.cors(cors -> cors.configurationSource(corsConfigurationSource()));
```

### 9.2 @CrossOrigin annotation

```java
@RestController
@CrossOrigin(origins = "https://example.com", maxAge = 3600)
public class ApiController {

    @CrossOrigin(origins = "*")  // override class-level
    @GetMapping("/public-data")
    public List<Data> publicData() { ... }
}
```

---

## 10. OAuth2 & OpenID Connect

### 10.1 OAuth2 flows được hỗ trợ

| Flow | Dùng khi | Spring Security hỗ trợ |
|---|---|---|
| Authorization Code | Web app, Mobile với PKCE | ✅ |
| Authorization Code + PKCE | SPA, Mobile | ✅ |
| Client Credentials | Service-to-service | ✅ |
| Implicit | Deprecated | ⚠️ |
| Device Authorization | IoT, CLI | ✅ |

### 10.2 OAuth2 Login (Resource Owner / Client)

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-client</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: ${GOOGLE_CLIENT_ID}
            client-secret: ${GOOGLE_CLIENT_SECRET}
            scope: openid, profile, email
          github:
            client-id: ${GITHUB_CLIENT_ID}
            client-secret: ${GITHUB_CLIENT_SECRET}
            scope: user:email
        provider:
          google:
            issuer-uri: https://accounts.google.com
```

```java
http.oauth2Login(oauth2 -> oauth2
    .loginPage("/login")
    .defaultSuccessUrl("/dashboard")
    .userInfoEndpoint(userInfo -> userInfo
        .userService(customOAuth2UserService)
    )
);
```

### 10.3 OAuth2 Resource Server (API bảo vệ bằng JWT)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
</dependency>
```

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth-server.example.com
          # Hoặc dùng JWKS URI trực tiếp:
          jwk-set-uri: https://auth-server.example.com/.well-known/jwks.json
```

```java
http
    .oauth2ResourceServer(oauth2 -> oauth2
        .jwt(jwt -> jwt
            .jwtAuthenticationConverter(jwtAuthConverter())
        )
    );

@Bean
public JwtAuthenticationConverter jwtAuthConverter() {
    JwtGrantedAuthoritiesConverter grantedAuthConverter = new JwtGrantedAuthoritiesConverter();
    grantedAuthConverter.setAuthorityPrefix("ROLE_");
    grantedAuthConverter.setAuthoritiesClaimName("roles");

    JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
    converter.setJwtGrantedAuthoritiesConverter(grantedAuthConverter);
    return converter;
}
```

### 10.4 OAuth2 Authorization Server (Spring Authorization Server)

```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-oauth2-authorization-server</artifactId>
</dependency>
```

```java
@Configuration
@Import(OAuth2AuthorizationServerConfiguration.class)
public class AuthServerConfig {

    @Bean
    public RegisteredClientRepository registeredClientRepository() {
        RegisteredClient client = RegisteredClient.withId(UUID.randomUUID().toString())
            .clientId("my-client")
            .clientSecret(passwordEncoder.encode("secret"))
            .clientAuthenticationMethod(ClientAuthenticationMethod.CLIENT_SECRET_BASIC)
            .authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
            .authorizationGrantType(AuthorizationGrantType.REFRESH_TOKEN)
            .authorizationGrantType(AuthorizationGrantType.CLIENT_CREDENTIALS)
            .redirectUri("https://app.example.com/callback")
            .scope(OidcScopes.OPENID)
            .scope("read")
            .tokenSettings(TokenSettings.builder()
                .accessTokenTimeToLive(Duration.ofHours(1))
                .refreshTokenTimeToLive(Duration.ofDays(30))
                .reuseRefreshTokens(false)
                .build())
            .build();

        return new InMemoryRegisteredClientRepository(client);
    }

    @Bean
    public JWKSource<SecurityContext> jwkSource() {
        RSAKey rsaKey = generateRsaKey();
        return new ImmutableJWKSet<>(new JWKSet(rsaKey));
    }
}
```

---

## 11. JWT (JSON Web Token)

### 11.1 Cấu trúc JWT

```
Header.Payload.Signature

eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9   ← Base64URL(Header)
.
eyJzdWIiOiJ1c2VyMTIzIiwicm9sZXMiOlsiVVNFUiJdLCJpYXQiOjE3MDAwMDAwMDAsImV4cCI6MTcwMDAwMzYwMH0
                                          ← Base64URL(Payload)
.
<signature>                               ← HMAC/RSA/EC signature
```

### 11.2 JWT Service implementation

```java
@Service
public class JwtService {

    @Value("${app.jwt.secret}")
    private String jwtSecret;

    @Value("${app.jwt.expiration:3600}")
    private long jwtExpiration;

    private SecretKey getSigningKey() {
        byte[] keyBytes = Decoders.BASE64.decode(jwtSecret);
        return Keys.hmacShaKeyFor(keyBytes);
    }

    // HS256: Dùng khi chỉ có 1 service cần verify token (shared secret).
    // RS256: Khuyến nghị cho production/OAuth2 vì public key có thể phân phát
    //        an toàn cho nhiều service mà không cần chia sẻ private key.
    public String generateToken(UserDetails userDetails) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("roles", userDetails.getAuthorities().stream()
            .map(GrantedAuthority::getAuthority)
            .collect(Collectors.toList()));

        return Jwts.builder()
            .claims(claims)
            .subject(userDetails.getUsername())
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + jwtExpiration * 1000))
            .signWith(getSigningKey(), Jwts.SIG.HS256)   // thay bằng RS256 cho distributed systems
            .compact();
    }

    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    public boolean isTokenValid(String token, UserDetails userDetails) {
        final String username = extractUsername(token);
        return username.equals(userDetails.getUsername()) && !isTokenExpired(token);
    }

    private boolean isTokenExpired(String token) {
        return extractClaim(token, Claims::getExpiration).before(new Date());
    }

    private <T> T extractClaim(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = Jwts.parser()
            .verifyWith(getSigningKey())
            .build()
            .parseSignedClaims(token)
            .getPayload();
        return claimsResolver.apply(claims);
    }
}
```

### 11.3 JWT Refresh Token Strategy

```java
@RestController
@RequestMapping("/auth")
public class AuthController {

    @PostMapping("/refresh")
    public ResponseEntity<TokenResponse> refresh(
            @RequestBody RefreshTokenRequest request) {

        RefreshToken refreshToken = refreshTokenService
            .findByToken(request.getRefreshToken())
            .orElseThrow(() -> new TokenRefreshException("Refresh token not found"));

        refreshTokenService.verifyExpiration(refreshToken);

        String accessToken = jwtService.generateToken(
            refreshToken.getUser());

        return ResponseEntity.ok(new TokenResponse(accessToken,
            refreshToken.getToken()));
    }

    @PostMapping("/logout")
    public ResponseEntity<?> logout(@RequestBody LogoutRequest request) {
        // Xóa refresh token từ DB để invalidate
        refreshTokenService.deleteByUserId(request.getUserId());
        return ResponseEntity.ok("Logged out");
    }
}
```

### 11.4 JWT Security Risks & Mitigations

| Rủi ro | Biện pháp |
|---|---|
| Token bị đánh cắp | Dùng HTTPS, lưu trong httpOnly cookie thay vì localStorage |
| Token không thể revoke | Dùng blacklist (Redis) hoặc short expiration + refresh token |
| Algorithm confusion (alg:none) | Luôn validate algorithm, không dùng `none` |
| Weak secret | Dùng key >= 256 bits cho HMAC, RSA >= 2048 bit |
| JWT in URL | Không đặt JWT trong query parameter |
| Clock skew | Cho phép sai số thời gian nhỏ (leeway) |

---

## 12. HTTP Basic & Digest Authentication

### 12.1 HTTP Basic

```java
http.httpBasic(basic -> basic
    .realmName("My App")
    .authenticationEntryPoint(customEntryPoint)
);
```

> ⚠️ **Lưu ý**: Credentials được gửi dưới dạng Base64 (không phải mã hóa). Phải dùng với HTTPS.

### 12.2 Digest Authentication

```java
// Digest auth – ít dùng hiện nay, không hỗ trợ tốt trong Spring Security 6+
DigestAuthenticationFilter digestFilter = new DigestAuthenticationFilter();
digestFilter.setUserDetailsService(userDetailsService);
digestFilter.setAuthenticationEntryPoint(digestEntryPoint());
http.addFilter(digestFilter);
```

---

## 13. LDAP Authentication

### 13.1 Embedded LDAP (test/development)

```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-ldap</artifactId>
</dependency>
<dependency>
    <groupId>com.unboundid</groupId>
    <artifactId>unboundid-ldapsdk</artifactId>
</dependency>
```

```java
@Bean
public EmbeddedLdapServerContextSourceFactoryBean contextSourceFactoryBean() {
    EmbeddedLdapServerContextSourceFactoryBean factory =
        EmbeddedLdapServerContextSourceFactoryBean.fromEmbeddedLdapServer();
    factory.setPort(8389);
    return factory;
}

@Bean
AuthenticationManager ldapAuthenticationManager(
        BaseLdapPathContextSource contextSource) {

    LdapBindAuthenticationManagerFactory factory =
        new LdapBindAuthenticationManagerFactory(contextSource);
    factory.setUserDnPatterns("uid={0},ou=people");
    factory.setUserDetailsContextMapper(new PersonContextMapper());
    return factory.createAuthenticationManager();
}
```

### 13.2 External LDAP / Active Directory

```yaml
spring:
  ldap:
    urls: ldap://ldap.example.com:389
    base: dc=example,dc=com
    username: cn=admin,dc=example,dc=com
    password: ${LDAP_PASSWORD}
```

```java
@Bean
public ActiveDirectoryLdapAuthenticationProvider adAuthProvider() {
    ActiveDirectoryLdapAuthenticationProvider provider =
        new ActiveDirectoryLdapAuthenticationProvider(
            "example.com",
            "ldap://ldap.example.com:389"
        );
    provider.setConvertSubErrorCodesToExceptions(true);
    provider.setUseAuthenticationRequestCredentials(true);
    return provider;
}
```

---

## 14. Remember-Me Authentication

### 14.1 Simple Hash-Based Token

```java
http.rememberMe(remember -> remember
    .key("uniqueAndSecretKey")   // dùng để hash token
    .tokenValiditySeconds(2592000)  // 30 ngày
    .rememberMeParameter("remember-me")
    .userDetailsService(userDetailsService)
);
```

> ⚠️ Token được lưu trong cookie và có thể bị tái sử dụng nếu bị đánh cắp.

### 14.2 Persistent Token (Khuyến nghị)

```java
@Bean
public PersistentTokenRepository persistentTokenRepository() {
    JdbcTokenRepositoryImpl repo = new JdbcTokenRepositoryImpl();
    repo.setDataSource(dataSource);
    repo.setCreateTableOnStartup(false);  // Tạo bảng thủ công
    return repo;
}

http.rememberMe(remember -> remember
    .tokenRepository(persistentTokenRepository())
    .tokenValiditySeconds(2592000)
);
```

SQL tạo bảng:
```sql
CREATE TABLE persistent_logins (
    username  VARCHAR(64)  NOT NULL,
    series    VARCHAR(64)  PRIMARY KEY,
    token     VARCHAR(64)  NOT NULL,
    last_used TIMESTAMP    NOT NULL
);
```

---

## 15. Method-Level Security

### 15.1 @PreAuthorize với SpEL nâng cao

```java
@Service
public class DocumentService {

    // Kiểm tra custom bean
    @PreAuthorize("@documentSecurity.canRead(authentication, #id)")
    public Document findById(Long id) { ... }

    // Kiểm tra dựa trên tham số
    @PreAuthorize("authentication.principal.organizationId == #orgId")
    public List<Document> findByOrganization(Long orgId) { ... }

    // Kết hợp nhiều điều kiện
    @PreAuthorize("hasRole('ADMIN') or " +
                  "(hasRole('USER') and #document.owner == authentication.name)")
    public void updateDocument(Document document) { ... }
}

@Component("documentSecurity")
public class DocumentSecurityEvaluator {
    public boolean canRead(Authentication auth, Long documentId) {
        // Logic phức tạp
        Document doc = documentRepository.findById(documentId).orElseThrow();
        return doc.isPublic() || doc.getOwner().equals(auth.getName()) ||
               auth.getAuthorities().stream()
                   .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
    }
}
```

### 15.2 Custom PermissionEvaluator

```java
@Component
public class CustomPermissionEvaluator implements PermissionEvaluator {

    @Override
    public boolean hasPermission(Authentication auth,
                                  Object targetDomainObject,
                                  Object permission) {
        if (targetDomainObject instanceof Document doc) {
            return switch (permission.toString()) {
                case "read"  -> doc.isPublic() || doc.getOwner().equals(auth.getName());
                case "write" -> doc.getOwner().equals(auth.getName());
                case "delete" -> hasRole(auth, "ADMIN");
                default -> false;
            };
        }
        return false;
    }

    @Override
    public boolean hasPermission(Authentication auth,
                                  Serializable targetId,
                                  String targetType,
                                  Object permission) {
        // Tải domain object từ DB theo targetId và targetType
        return false;
    }
}

// Dùng trong @PreAuthorize
@PreAuthorize("hasPermission(#document, 'write')")
public void updateDocument(Document document) { ... }
```

---

## 16. ACL (Access Control List)

### 16.1 Cấu hình ACL

```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-acl</artifactId>
</dependency>
```

```java
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class AclConfig {

    @Bean
    public AclService aclService() {
        return new JdbcMutableAclService(dataSource, lookupStrategy(), aclCache());
    }

    @Bean
    public AclAuthorizationStrategy aclAuthorizationStrategy() {
        return new AclAuthorizationStrategyImpl(
            new SimpleGrantedAuthority("ROLE_ADMIN"));
    }

    @Bean
    public PermissionGrantingStrategy permissionGrantingStrategy() {
        return new DefaultPermissionGrantingStrategy(new ConsoleAuditLogger());
    }
}
```

### 16.2 Cấp quyền ACL

```java
@Service
public class AclPermissionService {

    @Autowired
    private MutableAclService aclService;

    @Transactional
    public void grantPermission(Long resourceId, Class<?> resourceClass,
                                 String username, Permission permission) {
        ObjectIdentity oid = new ObjectIdentityImpl(resourceClass, resourceId);
        MutableAcl acl;
        try {
            acl = (MutableAcl) aclService.readAclById(oid);
        } catch (NotFoundException e) {
            acl = aclService.createAcl(oid);
        }

        Sid sid = new PrincipalSid(username);
        acl.insertAce(acl.getEntries().size(), permission, sid, true);
        aclService.updateAcl(acl);
    }
}
```

---

## 17. Security Events & Audit Logging

### 17.1 Lắng nghe các sự kiện xác thực

```java
@Component
@Slf4j
public class AuthenticationEventListener {

    @EventListener
    public void onSuccess(AuthenticationSuccessEvent event) {
        String username = event.getAuthentication().getName();
        log.info("LOGIN SUCCESS: user={}, ip={}",
            username, getClientIp(event));
    }

    @EventListener
    public void onFailure(AbstractAuthenticationFailureEvent event) {
        String username = event.getAuthentication().getName();
        String reason = event.getException().getMessage();
        log.warn("LOGIN FAILED: user={}, reason={}", username, reason);
        // Có thể ghi vào DB để track brute-force
    }

    @EventListener
    public void onLogout(LogoutSuccessEvent event) {
        log.info("LOGOUT: user={}", event.getAuthentication().getName());
    }
}
```

### 17.2 Custom AuthenticationFailureHandler

```java
@Component
public class CustomAuthFailureHandler implements AuthenticationFailureHandler {

    private final Map<String, AtomicInteger> failedAttempts = new ConcurrentHashMap<>();

    @Override
    public void onAuthenticationFailure(HttpServletRequest request,
                                         HttpServletResponse response,
                                         AuthenticationException exception)
            throws IOException {

        String username = request.getParameter("username");
        int attempts = failedAttempts
            .computeIfAbsent(username, k -> new AtomicInteger(0))
            .incrementAndGet();

        if (attempts >= 5) {
            // Lock account
            userService.lockAccount(username);
            response.sendError(HttpStatus.LOCKED.value(), "Account locked");
        } else {
            response.sendError(HttpStatus.UNAUTHORIZED.value(),
                "Invalid credentials. Attempts: " + attempts + "/5");
        }
    }
}
```

---

## 18. Các Lỗ Hổng Phổ Biến & Biện Pháp

### 18.1 Broken Access Control (OWASP A01:2021)

**Vấn đề**: Endpoint không kiểm tra authorization đúng cách.

```java
// ❌ Sai: Không kiểm tra ownership
@GetMapping("/api/orders/{id}")
public Order getOrder(@PathVariable Long id) {
    return orderRepository.findById(id).orElseThrow();
}

// ✅ Đúng: Kiểm tra ownership
@GetMapping("/api/orders/{id}")
@PreAuthorize("@orderSecurity.isOwner(authentication, #id)")
public Order getOrder(@PathVariable Long id) {
    return orderRepository.findById(id).orElseThrow();
}
```

### 18.2 Injection – SQL Injection

```java
// ❌ Sai: String concatenation trong JPQL/SQL
String query = "FROM User WHERE username = '" + username + "'";
entityManager.createQuery(query).getResultList();

// ✅ Đúng: Parameterized query
entityManager.createQuery("FROM User WHERE username = :username", User.class)
    .setParameter("username", username)
    .getResultList();
```

### 18.3 Cross-Site Scripting (XSS)

```java
// Spring Security thêm các security headers mặc định:
// X-Content-Type-Options: nosniff
// X-Frame-Options: DENY
// X-XSS-Protection: 0 (modern browsers dùng CSP thay thế)

// Thêm Content Security Policy (CSP)
http.headers(headers -> headers
    .contentSecurityPolicy(csp -> csp
        .policyDirectives("default-src 'self'; " +
                         "script-src 'self' 'nonce-{nonce}'; " +
                         "style-src 'self' 'unsafe-inline'; " +
                         "img-src 'self' data: https:;")
    )
);
```

### 18.4 Security Misconfiguration

```java
// ❌ Sai: Tắt security hoàn toàn
http.authorizeHttpRequests(auth -> auth.anyRequest().permitAll());

// ❌ Sai: Dùng wildcard quá rộng
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/admin**").hasRole("ADMIN")   // Chú ý: không có /
    .anyRequest().authenticated()
);
// "/adminEvil" vẫn match "/admin**"!

// ✅ Đúng
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/admin/**").hasRole("ADMIN")
    .anyRequest().authenticated()
);
```

### 18.5 Insecure Direct Object Reference (IDOR)

```java
// ❌ Sai: Trực tiếp dùng ID từ user input
@DeleteMapping("/files/{fileId}")
public ResponseEntity<?> deleteFile(@PathVariable Long fileId,
                                     Authentication auth) {
    fileService.delete(fileId);  // Không kiểm tra ownership!
    return ResponseEntity.ok().build();
}

// ✅ Đúng
@DeleteMapping("/files/{fileId}")
public ResponseEntity<?> deleteFile(@PathVariable Long fileId,
                                     @AuthenticationPrincipal UserDetails user) {
    File file = fileService.findById(fileId);
    if (!file.getOwner().equals(user.getUsername())) {
        throw new AccessDeniedException("Not authorized to delete this file");
    }
    fileService.delete(fileId);
    return ResponseEntity.ok().build();
}
```

### 18.6 Mass Assignment

```java
// ❌ Sai: Bind thẳng request body vào entity
@PostMapping("/users/{id}")
public User updateUser(@PathVariable Long id, @RequestBody User user) {
    user.setId(id);
    return userRepository.save(user);  // User có thể set isAdmin=true!
}

// ✅ Đúng: Dùng DTO riêng
@PostMapping("/users/{id}")
public User updateUser(@PathVariable Long id,
                        @RequestBody UpdateUserRequest request,
                        @AuthenticationPrincipal UserDetails currentUser) {
    User user = userRepository.findById(id).orElseThrow();
    // Chỉ update những field được phép
    user.setDisplayName(request.getDisplayName());
    user.setEmail(request.getEmail());
    return userRepository.save(user);
}
```

### 18.7 JWT Algorithm Confusion Attack

```java
// ❌ Sai: Không kiểm tra algorithm
JwtParser parser = Jwts.parser()
    .setSigningKeyResolver(signingKeyResolver)  // attacker có thể dùng alg=none
    .build();

// ✅ Đúng: Chỉ định algorithm cụ thể
JwtParser parser = Jwts.parser()
    .requireAlgorithm(Jwts.SIG.RS256.getId())  // Chỉ chấp nhận RS256
    .verifyWith(rsaPublicKey)
    .build();
```

### 18.8 Path Traversal

```java
// ❌ Sai: Dùng filename từ user input trực tiếp
@GetMapping("/files/{filename}")
public ResponseEntity<Resource> downloadFile(@PathVariable String filename) {
    Path filePath = Paths.get("/uploads/" + filename);
    Resource resource = new FileSystemResource(filePath);
    return ResponseEntity.ok(resource);
}
// Attacker có thể dùng: /files/../../etc/passwd

// ✅ Đúng: Validate và normalize path
@GetMapping("/files/{filename}")
public ResponseEntity<Resource> downloadFile(@PathVariable String filename) {
    Path uploadDir = Paths.get("/uploads").toAbsolutePath().normalize();
    Path filePath = uploadDir.resolve(filename).normalize();

    // Kiểm tra path không thoát khỏi upload directory
    if (!filePath.startsWith(uploadDir)) {
        throw new AccessDeniedException("Invalid file path");
    }

    Resource resource = new FileSystemResource(filePath);
    if (!resource.exists()) {
        throw new ResponseStatusException(HttpStatus.NOT_FOUND);
    }
    return ResponseEntity.ok(resource);
}
```

---

## 19. Spring Boot Auto-Configuration

### 19.1 Những gì Spring Boot tự cấu hình

Khi có `spring-boot-starter-security` trong classpath:

- Tạo `InMemoryUserDetailsManager` với user mặc định (`user` / random password in logs)
- Bật HTTP Basic authentication
- Bật Form login
- Bật CSRF protection
- Thêm security headers
- Bảo vệ tất cả endpoints

### 19.2 Properties cấu hình nhanh

```yaml
spring:
  security:
    user:
      name: admin
      password: ${ADMIN_PASSWORD}
      roles: ADMIN

    # OAuth2 (xem section 10)
    oauth2:
      client:
        registration: ...

    # Filter order
    filter:
      order: -100
```

### 19.3 Actuator Security

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health, info, metrics
  endpoint:
    health:
      show-details: when-authorized
```

```java
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/actuator/health", "/actuator/info").permitAll()
    .requestMatchers("/actuator/**").hasRole("ADMIN")
    .anyRequest().authenticated()
);
```

---

## 20. Testing Spring Security

### 20.1 Dependencies

```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-test</artifactId>
    <scope>test</scope>
</dependency>
```

### 20.2 Mock Authentication

```java
@SpringBootTest
@AutoConfigureMockMvc
class SecurityTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @WithMockUser(username = "testuser", roles = {"USER"})
    void authenticatedUserCanAccessProfile() throws Exception {
        mockMvc.perform(get("/profile"))
            .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(roles = {"ADMIN"})
    void adminCanAccessAdminPage() throws Exception {
        mockMvc.perform(get("/admin"))
            .andExpect(status().isOk());
    }

    @Test
    @WithAnonymousUser
    void anonymousUserCannotAccessProfile() throws Exception {
        mockMvc.perform(get("/profile"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    void loginWithValidCredentials() throws Exception {
        mockMvc.perform(formLogin("/login")
                .user("username", "testuser")
                .password("password", "secret"))
            .andExpect(authenticated().withUsername("testuser"))
            .andExpect(redirectedUrl("/dashboard"));
    }

    @Test
    void loginWithInvalidCredentials() throws Exception {
        mockMvc.perform(formLogin("/login")
                .user("username", "testuser")
                .password("password", "wrongpassword"))
            .andExpect(unauthenticated())
            .andExpect(redirectedUrl("/login?error"));
    }
}
```

### 20.3 Custom User Details trong Test

```java
@Retention(RetentionPolicy.RUNTIME)
@WithSecurityContext(factory = WithCustomUserSecurityContextFactory.class)
public @interface WithCustomUser {
    String username() default "testuser";
    long organizationId() default 1L;
    String[] roles() default {"USER"};
}

public class WithCustomUserSecurityContextFactory
        implements WithSecurityContextFactory<WithCustomUser> {

    @Override
    public SecurityContext createSecurityContext(WithCustomUser annotation) {
        CustomUserDetails userDetails = new CustomUserDetails(
            annotation.username(),
            annotation.organizationId(),
            Arrays.stream(annotation.roles())
                .map(r -> new SimpleGrantedAuthority("ROLE_" + r))
                .collect(Collectors.toList())
        );
        Authentication auth = new UsernamePasswordAuthenticationToken(
            userDetails, null, userDetails.getAuthorities());

        SecurityContext context = SecurityContextHolder.createEmptyContext();
        context.setAuthentication(auth);
        return context;
    }
}

// Dùng trong test
@Test
@WithCustomUser(username = "alice", organizationId = 42, roles = {"MANAGER"})
void managerCanViewOrgReports() throws Exception {
    mockMvc.perform(get("/reports/org/42"))
        .andExpect(status().isOk());
}
```

### 20.4 Test CSRF

```java
@Test
void postWithoutCsrfForbidden() throws Exception {
    mockMvc.perform(post("/api/data")
            .contentType(MediaType.APPLICATION_JSON)
            .content("{}"))
        .andExpect(status().isForbidden());
}

@Test
void postWithCsrfSucceeds() throws Exception {
    mockMvc.perform(post("/api/data")
            .with(csrf())
            .contentType(MediaType.APPLICATION_JSON)
            .content("{}"))
        .andExpect(status().isOk());
}
```

---

## 21. Best Practices & Checklist Production

### 21.1 Cấu hình bảo mật tổng thể

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class ProductionSecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            // 1. Xác thực
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**", "/actuator/health").permitAll()
                .anyRequest().authenticated()
            )

            // 2. Session (stateless cho API)
            .sessionManagement(s -> s
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))

            // 3. CSRF (tắt cho stateless API)
            .csrf(csrf -> csrf.disable())

            // 4. CORS
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))

            // 5. Headers
            .headers(headers -> headers
                .frameOptions(frame -> frame.deny())
                .contentSecurityPolicy(csp -> csp
                    .policyDirectives("default-src 'self'"))
                .httpStrictTransportSecurity(hsts -> hsts
                    .includeSubDomains(true)
                    .maxAgeInSeconds(31536000))
            )

            // 6. Exception handling
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint(jwtAuthEntryPoint)
                .accessDeniedHandler(customAccessDeniedHandler)
            )

            // 7. JWT filter
            .addFilterBefore(jwtAuthFilter,
                UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
```

### 21.2 Checklist Production

#### 🔐 Authentication
- [ ] Dùng `BCryptPasswordEncoder` với strength >= 12 (hoặc Argon2)
- [ ] Implement account lockout sau N lần đăng nhập sai
- [ ] Require MFA (Multi-Factor Authentication) cho tài khoản quan trọng
- [ ] JWT secret >= 256 bits, lưu trong vault (không hardcode)
- [ ] Access token expiry ngắn (15-60 phút), dùng refresh token
- [ ] Refresh token lưu trong DB để có thể revoke

#### 🛡️ Authorization
- [ ] Kiểm tra authorization ở cả URL level VÀ method level
- [ ] Không dùng role/permission dựa trên URL pattern thiếu chính xác
- [ ] Kiểm tra object-level authorization (IDOR)
- [ ] Không expose thông tin nhạy cảm trong error messages

#### 🌐 Transport Security
- [ ] Bật HTTPS cho tất cả môi trường (không chỉ production)
- [ ] Bật HSTS (Strict-Transport-Security)
- [ ] Certificate rotation plan
- [ ] TLS 1.2+ only (disable TLS 1.0, 1.1, SSL 3.0)

#### 📝 Session & Cookie
- [ ] Cookie: `HttpOnly=true`, `Secure=true`, `SameSite=Strict`
- [ ] Session fixation protection bật
- [ ] Session timeout phù hợp với mức độ nhạy cảm
- [ ] Logout thực sự invalidate session

#### 🔒 Headers
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY` hoặc `SAMEORIGIN`
- [ ] `Content-Security-Policy` nghiêm ngặt
- [ ] `Referrer-Policy: strict-origin-when-cross-origin`
- [ ] Xóa `Server`, `X-Powered-By` headers

#### 📊 Monitoring & Audit
- [ ] Log đầy đủ: đăng nhập thành công/thất bại, logout, thay đổi quyền
- [ ] Không log credentials hoặc thông tin nhạy cảm
- [ ] Alert khi có anomaly (quá nhiều login fail, unusual access patterns)
- [ ] Dùng security event listeners của Spring Security

#### 🔄 Dependencies
- [ ] Theo dõi CVEs liên quan đến Spring Security
- [ ] Dùng Spring Boot BOM để quản lý version
- [ ] Chạy `./mvnw dependency:check` hoặc Snyk/Dependabot
- [ ] Cập nhật dependencies thường xuyên

### 21.3 Spring Security Headers mặc định

Spring Security tự động thêm các header bảo mật sau:

```
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000; includeSubDomains (chỉ HTTPS)
X-Frame-Options: DENY
X-XSS-Protection: 0
```

Tùy chỉnh:

```java
http.headers(headers -> headers
    .defaultsDisabled()   // Tắt tất cả defaults
    .cacheControl(Customizer.withDefaults())
    .contentTypeOptions(Customizer.withDefaults())
    .frameOptions(frame -> frame.sameOrigin())
    .httpStrictTransportSecurity(hsts -> hsts
        .includeSubDomains(true)
        .preload(true)
        .maxAgeInSeconds(31536000)
    )
);
```

---

## Tài liệu tham khảo

- [Spring Security Reference Documentation](https://docs.spring.io/spring-security/reference/)
- [Spring Security Architecture](https://spring.io/guides/topicals/spring-security-architecture)
- [OWASP Top Ten 2021](https://owasp.org/www-project-top-ten/)
- [OWASP Spring Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Spring_Security_Cheat_Sheet.html)
- [Spring Authorization Server](https://docs.spring.io/spring-authorization-server/reference/)
- [JWT Best Practices (RFC 8725)](https://www.rfc-editor.org/rfc/rfc8725)
- [NIST Password Guidelines (SP 800-63B)](https://pages.nist.gov/800-63-3/sp800-63b.html)
