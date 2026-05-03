 A steganographic data transmission system exploiting Spotify playlist track ordering

---
## 1.0 Abstract

### 1.1 Overview

Outloud is a Proof-of-Concept (PoC) covert channel that encodes arbitrary text 
messages into the ordering of tracks within a public Spotify playlist.

By exploiting the fact that Spotify embeds all playlist track URIs in publicly 
accessible HTML meta tags, a receiver requires no authentication whatsoever to 
decode messages. The sender encodes data using a `base-N positional encoding scheme`  where the first N tracks define a dynamic codebook, and subsequent tracks represent encoded characters.

The shared secret between sender and receiver is a single integer, the `sync length`, 
which determines both the codebook and the encoding base.

This paper documents the technical design, implementation, API reverse engineering 
findings, and detection considerations for this channel.

Follow this and additional works at: https://1kb2.xyz

---

### 1.2 What is a Covert Channel?

**Covert channels** [1] enable secret data transmission through legitimate system resources or protocols, evading detection by hiding communication within normal operations. They fall into:
* **Timing channels** [2], like inter-packet delays.
* **Storage channels** [3], like modifying packet headers or in our case exploiting Spotify playlist track ordering.

---

### 1.3 Why Spotify?

Spotify presents a uniquely attractive platform for covert channel implementation for several reasons. With over 761 million users [4], playlist activity is considered entirely normal behavior that generates no suspicion. Unlike email or messaging platforms, playlist modifications leave no obvious communication trail between two parties.

More critically, Spotify exposes all playlist track URIs in publicly accessible HTML meta tags:
```html
<SNIP>
<meta name="music:song" content="https://open.spotify.com/track/7o2AeQZzfCERsRmOM86EcB"/>
<meta name="music:song:track" content="1"/>
<meta name="music:song" content="https://open.spotify.com/track/4Sxv0whUHWzHK5T8uuP66S"/>
<meta name="music:song:track" content="2"/>
<SNIP>
```

intended for search engine indexing and social media link previews. This means a receiver can decode messages using nothing more than an HTTP request to a public playlist URL, no account, no API key, no authentication of any kind, for public playlists only.

Finally, Spotify's internal GraphQL API accepts write operations such as adding and removing tracks using session tokens extractable from any logged-in browser session, requiring no registered developer account or official API access.

---

## 2.0 Background

Steganography is the practice of concealing information within ordinary, non-secret data so that the existence of a message goes undetected [5]. 

While steganographic techniques have existed for centuries, the field only developed a formal theoretical foundation in the early 1990s with the rise of digital media and networked communication [5].
### 2.1 Steganography theory

Unlike cryptography, which protects the content of a message, steganography protects the fact that communication is occurring at all. 

Steganography is sometimes conflated with security through obscurity, the flawed principle that a system is secure simply because its inner workings are hidden. 
### 2.2 Existing covert channels (DNS, HTTP headers, timing)
### 2.3 Why social platforms are interesting targets


---

## 3.0 Technical Design

### 3.1 The sync header concept
### 3.2 Base-12 encoding
### 3.3 SYNC_LENGTH as shared secret
### 3.4 Channel capacity analysis

---

## 4.0 Implementation

### 4.1 Receiver: zero-auth HTML meta tag scraping
### 4.2 Sender: internal GraphQL API reverse engineering
### 4.3 Human sleep intervals for evasion

---

## 5.0 Findings

### 5.1 Spotify embeds all track URIs in public HTML
### 5.2 client-token is not account-bound
### 5.3 Bearer token required for writes only
### 5.4 No rate limiting observed during testing

---

## 6.0 Detection, Mitigation & Expansion

### 6.1 Blue team perspective
### 6.2 What would trigger a SIEM
### 6.3 How Spotify could detect/prevent this
### 6.4 What other social platforms can be exploited?

---

## 7.0 Conclusion

---

## References

[1] Taylor & Francis Knowledge Hub Page on Covert Channels, https://taylorandfrancis.com/knowledge/Engineering_and_technology/Computer_science/Covert_channels/

[2] Wray, J. C. (1991). "An Analysis of Covert Timing Channels." _Proceedings of the IEEE Symposium on Research in Security and Privacy_, 313–323. Oakland, CA, https://www.cs.cornell.edu/people/vickyw/iFlow/papers/wra91.pdf

[3] Lampson, B. W. (1973). "A Note on the Confinement Problem." _Communications of the ACM_, 16(10), 613–615. https://doi.org/10.1145/362375.362389

[4] Spotify, "Company Info", https://newsroom.spotify.com/company-info/

[5] Fridrich, J. (2009). Steganography in Digital Media: Principles, Algorithms, and Applications. Cambridge University Press, https://books.google.it/books?id=wcAZ-QEthqkC&printsec=frontcover#v=onepage&q&f=false

[6] Schneier, B. (2000). Secrets and Lies: Digital Security in a Networked World. Wiley. page 344 https://archive.org/details/secretsliesdigit0000schn/

[7] MITRE ATT&CK (T1102) https://attack.mitre.org/techniques/T1102/



TOCLASS 

Existing web service abuse techniques (MITRE ATT&CK T1102 [7]) typically store malicious payloads directly on legitimate platforms such as Dropbox, GitHub, or Pastebin. While these blend into normal traffic, the payload itself remains detectable through content inspection.

Outloud differs fundamentally, no malicious content is stored anywhere. The 
message exists only in the semantic ordering of tracks within a normal music playlist, invisible to any content-based detection.
